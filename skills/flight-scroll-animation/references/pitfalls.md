# Pitfalls (found the hard way, on the Vesper/MG Webdesigner and STACKED builds)

## 0. Shipping the scrub to mobile and finding out afterwards

The most expensive mistake with this pattern is not a bug in the code — it
is building the whole hero as a scrub, shipping it, and only then learning
that it feels bad on a phone. It cost a full rework on the STACKED build:
mobile got scroll-driven crossfading stills, then the user came back wanting
the video playing in a loop instead, which meant a *third* encode and a
restructured section.

Everything about the effect that makes it good on desktop works against it
on touch: seeking stutters during momentum scroll, the dense-keyframe encode
is heavy on cell data, and the 400-500vh section is several empty screens of
scrolling on a small viewport.

**Fix**: treat the mobile behavior as a question to settle with the user
*before* generating footage — see "Decide the mobile behavior FIRST" in
SKILL.md. The answer determines how many encodes you produce and how the
section is structured, so it is not a decision that can be retrofitted
cheaply.

Two things that look like solutions but are not:

- **Reversing video in JS.** Negative `playbackRate` is effectively
  unsupported, and stepping `currentTime` backwards each frame is the same
  seeking that was already too slow. Bake the ping-pong into the file with
  ffmpeg instead.
- **Leaving `src` in the HTML and just hiding the video with CSS.** The file
  still downloads. Every phone pays the full cost of an effect it will never
  run. Assign `src` from JS once the mode is known.

## 1. Camera-mismatched keyframes make the building slide across the ground

When the footage is built by chaining image-to-video clips between approved
stills (`start_image` → `end_image`), the two stills of any one pair **must
be framed from the same camera position**. If they are not, the model has no
way to land on the end frame except to translate, rotate and rescale the
subject on its way there — so a house physically slides across its own plot,
the boundary wall jumps sideways, and the whole shot reads as fake. This was
caught by the user, not by me, on the VÉRTICE build: "a casa desliza de
forma impossível e incongruente."

The trap is that the stills each look *great on their own*. The defect only
exists in the relationship between them, so reviewing the stills one by one
will not surface it — and neither will re-rolling the video seed, because
the geometry gap is the cause, not the sampling.

**Do not** try to fix this with prompt wording. "Locked-off camera", "the
building never moves", "static tripod" — all of it loses to a mismatched end
frame, because reaching that frame is a hard constraint and the wording is
not.

**Check before spending credits on the clip.** Average the two stills
together; a well-registered pair ghosts into one building, a bad pair shows
two:

```bash
ffmpeg -y -i fase-04.jpg -i fase-05.jpg -filter_complex \
  "[0:v]scale=800:450[a];[1:v]scale=800:450[b];[a][b]blend=all_mode=average" \
  -frames:v 1 overlay.jpg
```

**Fix**: regenerate the *destination* still using the origin still as the
reference image, with a prompt that changes only the subject's state and
freezes everything else — "change ONLY the state of the construction; camera
position, focal length, framing, horizon line and perspective are identical
to the reference; do not move, rotate, rescale or reframe anything." Then
regenerate every clip that touched the replaced still (the one ending on it
*and* the one starting from it — forgetting the second is easy).

Two related habits worth keeping:

- **Generate all the phase stills against one anchor** (the finished hero
  shot), which keeps the subject consistent — but note that a shared anchor
  does *not* guarantee a shared camera. Verify each consecutive pair anyway.
- **Don't put people in the prompt of a calm clip.** "The last workers leave
  the garden" produced a swarm of blurred red figures that dissolved on the
  doorstep — worse than the problem it was decorating. Ask explicitly for
  "no people, no vehicles" when the shot is meant to be serene. Fast-motion
  worker blur is fine and authentic *during* the construction phases; it is
  not fine on a finished-house beauty shot.

## 2. Don't gate the scrub assignment on a variable set only by `loadedmetadata`

First version of the code looked like this:

```js
var duration = 0;
vidA.addEventListener('loadedmetadata', function(){ duration = vidA.duration; startIdle(); }, {once:true});
// ...later, in the scroll handler:
if(duration){ vidA.currentTime = progress * duration; }
```

This silently does nothing if the user starts scrolling before that one
`loadedmetadata` event has fired — `duration` is still `0`, the `if` is
false, the assignment never runs, and there's no error to notice. On a slow
connection or a large preload, this window can be longer than you'd think.

**Fix**: read the video element's own `.duration` property live, every
time, instead of caching it in a closure variable that depends on a
one-time event having already fired:

```js
if(vidA.duration){ vidA.currentTime = progress * vidA.duration; }
```

`vidA.duration` is `NaN` (falsy-ish, but actually needs an explicit check —
`NaN` is not falsy in a way `if()` treats consistently across engines, so
prefer `if(!isNaN(vidA.duration) && vidA.duration)` if you want to be
extra-safe) until metadata is ready, and a real number after — no separate
tracking variable needed, and it can never go stale.

## 3. Clear the crossfade timer *before* switching to scrub mode, not after

The idle-mode crossfade scheduler (`scheduleCrossfade`) sets a `setTimeout`
that, when it fires, resets `currentTime = 0` and calls `.play()` on the
"next" video. If the user starts scrolling (entering scrub mode) and that
timer is still pending, it can fire *during* the scrub — silently resetting
the very `currentTime` the scroll handler just set, and un-pausing a video
that's supposed to be a paused scrub target.

**Fix**: `clearTimeout(scheduleTimer)` as the very first thing that happens
when transitioning `mode` from `'idle'` to `'scrub'` (see the state machine
code in SKILL.md — the comment marks exactly where). Symmetrically,
`startIdle()` (called when leaving the scrub zone) re-arms its own timer via
`scheduleCrossfade`, so there's no need to clear anything on the way back —
just make sure `mode` is set *before* calling anything that checks it.

## 4. The origin must support HTTP Range requests for smooth seeking

Setting `video.currentTime` repeatedly (scrubbing) needs the browser to be
able to fetch arbitrary byte ranges of the file, which needs the server to
respond to `Range:` headers with `206 Partial Content`. Python's built-in
`python -m http.server` (used for quick local preview) does **not**
reliably support this — seeks can silently fail to move `currentTime` at
all even though the whole file is already buffered. This is a *local
preview server* limitation, not a bug in the page: Vercel (and virtually
every real static host/CDN) serves `206` responses correctly, confirmed by
checking the network log after deploying — video requests come back `206`
in production even when they were failing to seek against the local dev
server.

If local scrub testing seems broken, check the response status/headers for
the video request before assuming the JS is wrong.

The diagnostic signature is distinctive, and worth recognizing fast because
it looks exactly like a broken seek: `readyState === 4`
(HAVE_ENOUGH_DATA) and `buffered.end(0)` covering nearly the whole clip, yet
`currentTime` stays pinned at `0` after assignment. Fully loaded, refuses to
seek — that combination means the origin, not the page. Confirm with
`fetch(src, {headers:{Range:'bytes=0-99'}})` and check for a `206`; against
Vercel it comes back `206` with a `content-range` header.

## 5. Verifying this in a non-composited/headless browser tool

Some automated browser tooling can have a tab that never actually composites
frames (`document.visibilityState` stays `"hidden"` indefinitely, a
`screenshot` call times out saying the pane "is not displayed"). Two
knock-on effects, both easy to misdiagnose as page bugs:

- `requestAnimationFrame` callbacks may never fire for a hidden tab (this is
  normal browser power-saving behavior, not specific to any one tool) — so
  a scroll listener that gates work behind `requestAnimationFrame` can look
  completely dead even though the code is correct. Test by temporarily
  overriding `window.requestAnimationFrame = function(cb){ cb(); return 0;
  }` before dispatching a synthetic `scroll` event, so the callback runs
  synchronously instead of waiting on a frame that will never come.
- Setting `.currentTime` and reading it back *immediately* (same
  microtask/synchronous line) is not reliable even in a normal visible tab —
  seeking is asynchronous. Wait for the `seeked` event, or at minimum a
  short `setTimeout`, before asserting the new value stuck.

When you hit this limitation, say so explicitly to whoever you're building
for rather than reporting "verified" — confirm the *logic* (mode
transitions, pause state, class toggling) via assertions, and ask them to
eyeball the final scroll feel on the deployed link, since that's the one
thing that genuinely can't be confirmed without a compositing viewport.
