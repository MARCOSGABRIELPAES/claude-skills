---
name: flight-scroll-animation
description: Build a scroll-scrubbed "flight-through" hero video — where the video's playback position is tied directly to scroll position, so the user seems to fly the camera through a space (a building walkthrough, a product reveal, an Apple-product-page-style hero) as they scroll, with an ambient looping/crossfading state when not actively scrolling. Use this whenever the user asks for a "flight scrolling animation", a scroll-scrubbed or scroll-controlled video, a video that "plays as I scroll", a room-by-room walkthrough tied to scroll, or a parallax/cinemagraph hero that should feel alive at rest and directable while scrolling. Also covers the mobile question this technique always raises — scrubbing is desktop-only in practice, so the skill decides the touch-device behavior (self-playing ping-pong loop, crossfading stills, or scrub anyway) with the user BEFORE building, and carries the ffmpeg recipe for baking a forward-and-back loop into the file.
---

# Flight scroll animation

Ties a `<video>` element's `currentTime` to scroll position inside a tall
sticky section, so scrolling *is* scrubbing the video — the classic
Apple-product-page hero technique, generalized to any "camera glides through
a space as you scroll" brief (architectural walkthroughs, product reveals,
before/after transitions).

On a pointer device this has two distinct visual states that are easy to
conflate but need separate handling (touch devices get their own behavior
entirely — see the next section, and settle it before you build):

1. **Idle** — the user hasn't reached the scroll-active zone yet (or has
   scrolled past it). The video should still feel alive: play normally,
   looped, ideally with a seamless crossfade at the loop point rather than a
   visible jump-cut.
2. **Scrub** — the user is scrolling inside the flight section. The video is
   *paused* and its `currentTime` is driven directly by scroll progress.
   Nothing should be "playing" here — every frame is a deliberate scrub
   target, not a moving playhead.

Getting the mode transition right (and cleaning up the other mode's state
when switching) is most of the actual difficulty here — see "The state
machine" below for the bug that's easy to introduce.

## Decide the mobile behavior FIRST — and ask before building

**Scroll-scrubbing is a desktop technique.** On touch devices it ranges from
mediocre to broken, and this is not something to discover after the build:

- iOS Safari (and mobile Chrome to a lesser degree) stutters or silently
  ignores rapid `currentTime` assignment during momentum scrolling. The
  scrub reads as laggy or frozen, not as camera control.
- Scrubbing needs a **dense-keyframe** encode, which is far heavier than a
  normal encode of the same footage — a 1080p flight file lands around
  15-20MB. That is a lot to push over mobile data for a hero.
- The tall scroll section (400-500vh) that the effect requires means several
  full screens of scrolling on a phone before the visitor reaches any actual
  content.

So **raise this with the user up front, before generating footage or writing
the page**, rather than shipping a desktop-only effect and waiting for them
to report that mobile feels wrong. Detect that the brief will have mobile
visitors (it always will, unless they say otherwise), then ask which mobile
behavior they want. The realistic options:

1. **Self-playing ping-pong loop (recommended default).** The video plays
   forward then backward on repeat, ignoring scroll entirely. Keeps the
   footage as the hero, feels alive, costs nothing in scroll length. See
   "Mobile fallback" below.
2. **Scroll-driven crossfading stills.** The 4-6 source stills fade between
   each other as the visitor scrolls. Preserves the "scroll drives the
   narrative" idea and is very light, but loses the motion.
3. **Keep the scrub on mobile anyway.** Only if they explicitly accept the
   jank and the download; say plainly that it will not feel like it does on
   desktop.

Ask with a real question, not a rhetorical one — the answer changes what
footage you generate (a ping-pong loop wants a separate lighter encode) and
how the section is structured, so getting it after the fact means redoing
both.

## Mobile fallback: bake the ping-pong into the file

Do **not** try to play a video backwards in JavaScript. Negative
`playbackRate` is unsupported in practice, and driving reverse playback by
assigning `currentTime` every frame reintroduces exactly the seeking problem
that made scrubbing unusable on mobile in the first place.

Instead concatenate the clip with a reversed copy of itself, so a plain
native `loop` gives you a seamless forward-and-back cycle with no JS touching
frames at all. Encode it separately from the scrub file: this one is never
seeked, so it does **not** need dense keyframes and compresses far better —
on the STACKED build the same footage went from 19MB (1080p, `-g 12`) to
4.4MB (720p, default GOP), a 77% saving.

```bash
# forward + reversed, one seamless loop. trim=start_frame=1 drops the
# duplicated frame at the seam.
ffmpeg -y -i flight.mp4 \
  -filter_complex "[0:v]scale=1280:720:flags=lanczos,split[f][t];\
[t]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[f][r]concat=n=2:v=1[out]" \
  -map "[out]" -c:v libx264 -preset slow -crf 27 -pix_fmt yuv420p \
  -movflags +faststart -an \
  flight-loop.mp4
```

`reverse` buffers the whole clip in memory — fine for the 10-15s a hero
needs, not for long footage.

### Frame it for portrait — don't let `object-fit:cover` do it for you

The `scale=1280:720` above keeps the loop landscape, same as the source. If
the loop is then displayed full-bleed in a tall mobile container (a 100vh
hero, `object-fit:cover`), the crop math gets brutal: a 16:9 clip in a
~0.46-aspect phone viewport shows only ~25-30% of the frame's *width*,
centered — mostly whatever happened to be at the horizontal middle, usually
a sliver of sky and water with the actual subject reduced to a thin strip.
This is not a subtle effect; it reads as "video is framed wrong," and it's
easy to ship without noticing because it looks fine in a normal browser
window (`(hover:none)` is false there, so it's rendering the desktop scrub
path, not the mode you actually need to check).

Fix it in two parts, together — doing only one still leaves the other
problem:

1. **Pre-crop the source to a portrait-friendly aspect** (e.g. 4:5) with
   the region you actually want kept, *before* the reverse/concat step.
   Extract a few real frames across the clip's duration and eyeball the
   crop candidate first — a static assumption about where the subject sits
   rarely survives contact with a multi-shot camera move:

   ```bash
   # sample frames to check framing before committing to a crop
   ffmpeg -y -ss 3.5 -i flight.mp4 -vframes 1 -q:v 3 check_3.5.jpg
   # candidate crop: drop CROPY px of dead space off the top, keep CROPH tall
   ffmpeg -y -i check_3.5.jpg -vf "crop=1920:CROPH:0:CROPY,scale=-2:1200,crop=960:1200:(iw-960)/2:0" -q:v 3 preview.jpg
   ```

   Fold the working `crop=...,scale=...` values into the real encode, ahead
   of the existing `scale=1280:720` step (replace it, don't stack both).

2. **Give the mobile video its own box sized to that same aspect ratio**
   (`aspect-ratio: 4/5`), instead of forcing it to fill `100vh`. If the crop
   is baked in at 4:5 and the display box is also 4:5, `object-fit:cover`
   has nothing left to crop — the composed frame shows exactly as designed,
   on every phone width, with no further runtime surprises. This usually
   means the video can no longer be an absolutely-positioned full-bleed
   background behind overlaid text — split it into its own stage element and
   let the heading/CTA flow in normal document flow *below* it (on a solid
   panel) rather than fighting a now-shorter video for legibility. That's a
   real layout change, not just a CSS tweak, so budget for it rather than
   trying to patch it in with `object-position`.

In loop mode the section must also **stop being a scroll container**, or the
visitor still scrolls four empty screens for an effect that is not running:

```css
body.film-loop-mode .film{height:auto;}          /* was 420vh */
body.film-loop-mode .film-sticky{position:relative;}  /* was sticky */
```

If the flight has chapter captions, drive them off the video instead of off
scroll — map `currentTime` so they run forward on the way out and backward
on the way home, matching what is on screen:

```js
function chapterFromLoopTime(){
  var d = vid.duration; if(!d || isNaN(d)) return;
  var half = d / 2, t = vid.currentTime;
  var p = t <= half ? (t / half) : (1 - (t - half) / half);  // 0→1→0
  setChapter(Math.min(last, Math.max(0, Math.floor(p * chapterCount))));
}
vid.addEventListener('timeupdate', function(){
  if(filmMode === 'loop'){ chapterFromLoopTime(); }
});
```

## Picking the mode

Resolve to one of three behaviors at load, and re-resolve on resize — but
only act when the *class of device* actually changed, because a mobile URL
bar hiding fires `resize` constantly and must not restart the film:

```js
function pickFilmMode(){
  if(matchMedia('(prefers-reduced-motion: reduce)').matches) return 'static';
  if(matchMedia('(hover: none)').matches) return 'loop';   // phones + tablets
  if(matchMedia('(max-width: 900px)').matches) return 'loop';
  return 'scrub';
}
```

`(hover: none)` is the honest touch test — `max-width` alone misses tablets,
and `maxTouchPoints` misfires on touchscreen laptops that scrub fine.

Three consequences worth wiring deliberately:

- Set each mode's `src` **in JS, not in the HTML** (`data-src` + assign on
  activation). Otherwise every phone downloads the heavy scrub encode before
  your mode logic ever runs, which is the exact cost the fallback exists to
  avoid. Verify with `video.getAttribute('src') === null` and
  `networkState === 0` at mobile width.
- `prefers-reduced-motion` deserves its own mode, not a share of the loop
  mode: an autoplaying looping video is precisely what that setting asks you
  not to do. Show a still. And check that whatever you show in that mode is
  genuinely static — a decorative Ken Burns drift on the fallback image
  quietly defeats the whole point.
- Keep opacity fades under reduced motion (they do not trigger motion
  sensitivity); drop the zooms, drifts and translates.

## Structure

```html
<section class="hero" id="hero" style="height:420vh;">   <!-- tall: scroll room -->
  <div class="hero-sticky" style="position:sticky; top:0; height:100vh; overflow:hidden;
       background:url('poster.jpg') center/cover no-repeat;">  <!-- floor, see below -->
    <video id="videoA" class="hero-video is-active" muted playsinline preload="auto"
           poster="poster.jpg" src="flight.mp4"></video>
    <video id="videoB" class="hero-video" muted playsinline preload="auto" src="flight.mp4"></video>
    <!-- scrim, wordmark, content overlay on top, z-index above the video layers -->
  </div>
</section>
```

The section height (`420vh` above) controls how much scroll distance maps to
the full video duration — taller = slower/more deliberate scrub, shorter =
faster. Tune per how much footage there is to cover.

`background: url(poster) center/cover` on the sticky container is not
decorative — it's the fallback that keeps the hero from ever looking blank
if the video is slow to become visible (see `references/pitfalls.md`).

## The state machine

```js
var mode = 'idle'; // 'idle' | 'scrub'
var current = vidA, idle = vidB;
var scheduleTimer = null;

function scheduleCrossfade(active){
  clearTimeout(scheduleTimer);
  if(!active.duration) return;
  var rate = active.playbackRate || 1;
  var FADE = 1.2; // seconds, matches the CSS opacity transition duration
  var ms = Math.max((active.duration - FADE) / rate * 1000, 200);
  scheduleTimer = setTimeout(function(){
    if(mode !== 'idle') return;               // scrub mode may have taken over meanwhile
    var next = active === vidA ? vidB : vidA;
    next.currentTime = 0; next.play().catch(function(){});
    next.classList.add('is-active'); active.classList.remove('is-active');
    current = next; idle = active;
    scheduleCrossfade(current);
  }, ms);
}

function startIdle(){
  mode = 'idle';
  current.classList.add('is-active'); idle.classList.remove('is-active');
  current.play().catch(function(){});
  scheduleCrossfade(current);
}

var rafPending = false;
function updateOnScroll(){
  rafPending = false;
  var rect = heroSection.getBoundingClientRect();
  var scrollable = heroSection.offsetHeight - window.innerHeight;
  var progress = scrollable > 0 ? Math.max(0, Math.min(1, -rect.top / scrollable)) : 0;
  var inFlightRange = progress > 0.002 && progress < 0.998;

  if(inFlightRange){
    if(mode !== 'scrub'){
      mode = 'scrub';
      clearTimeout(scheduleTimer);          // <-- critical, see pitfall #3 below
      vidA.pause(); vidB.pause();
      vidA.classList.add('is-active'); vidB.classList.remove('is-active');
      current = vidA;
    }
    if(vidA.duration){ vidA.currentTime = progress * vidA.duration; }  // <-- pitfall #2
  } else if(mode !== 'idle'){
    vidA.currentTime = 0;
    startIdle();
  }
}
window.addEventListener('scroll', function(){
  if(!rafPending){ rafPending = true; requestAnimationFrame(updateOnScroll); }
}, {passive:true});
```

Before wiring the scroll listener, set `vidA.playbackRate = vidB.playbackRate
= <rate>` if the brief wants slow-motion idle playback (e.g. "0.6x for
calm") — and make sure `scheduleCrossfade`'s timing math divides by that
rate, not just the raw video duration, or the crossfade will fire too early
relative to actual wall-clock playback.

Read `references/pitfalls.md` before shipping this — it documents two real
bugs hit building this pattern the first time, both subtle enough to pass a
casual glance at the code.

## Generating the source footage

If the flight video itself needs generating (rather than being supplied),
use an image-to-video model that accepts multiple reference stills — pass
the hero/start frame as `start_image` and 3-5 of the destination-room stills
as `image_references`, and write the prompt as one continuous camera move
naming each space in the order the camera should pass through it ("...glides
through the glass wall into the great room, revealing... continues floating
onward into the kitchen... settles on..."). This keeps the generated motion
anchored to real, already-approved stills instead of inventing new rooms.
For a **progression** rather than a flight — a construction timelapse, a
before/after, anything where the subject changes state instead of the camera
travelling — do not ask one clip to cover the whole arc. Generate an approved
still per stage, then generate one short clip per *consecutive pair* with the
stills as `start_image`/`end_image`, and concatenate. Every clip is guaranteed
to begin and end on a frame you already signed off, the joins are
frame-accurate, and it is far cheaper than one long generation (on the VÉRTICE
build, 5×5s at Kling 3.0 `pro` with `sound:"off"` cost ~44 credits against ~90
for a single 10s Seedance clip that could not be steered through the stages at
all).

Drop the duplicated boundary frame when concatenating, or every join stutters:

```bash
ffmpeg -y -i c1.mp4 -i c2.mp4 -i c3.mp4 -filter_complex \
  "[0:v]setpts=PTS-STARTPTS[v0];\
[1:v]trim=start_frame=1,setpts=PTS-STARTPTS[v1];\
[2:v]trim=start_frame=1,setpts=PTS-STARTPTS[v2];\
[v0][v1][v2]concat=n=3:v=1[out]" -map "[out]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an master.mp4
```

**Before generating any clip in that chain, verify that each pair of stills is
framed from the same camera position** — otherwise the model slides the
subject across the frame to reach the end image, and no prompt wording will
stop it. That is pitfall #1 in `references/pitfalls.md`, with the ffmpeg
overlay check and the fix; read it before spending credits, and inspect the
finished clips frame-by-frame rather than trusting that approved stills imply
an approved clip.

See the `one-page-site-builder` skill's `asset-generation.md` for the
model-resolution and batching workflow, and re-encode with **dense
keyframes** before shipping (below) — this matters more here than for a
normal autoplay video, because scrubbing needs a keyframe near every
scroll-target time or seeks look laggy/jump to the wrong frame:

```bash
ffmpeg -y -i raw.mp4 -vf "scale=1920:1080:flags=lanczos" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -g 12 -keyint_min 12 -sc_threshold 0 -movflags +faststart -an \
  flight.mp4
```

## Reference files

- `references/pitfalls.md` — starts with the two expensive ones (shipping the
  scrub to mobile and finding out afterwards; camera-mismatched keyframes that
  make the subject slide across the ground), then the two real code bugs
  (stale-duration gate, and the crossfade-timer race), plus the
  server/Range-request and headless-browser-testing caveats.
