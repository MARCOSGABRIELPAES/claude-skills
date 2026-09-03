# Asset generation workflow (Higgsfield-style image/video MCP)

Applies to any MCP that exposes `generate_image`, `generate_image_batch`,
`generate_video`, `generate_video_batch`, `models_explore`, `jobs_wait`,
`balance`, `show_generation_by_ids` (tool names are typically prefixed with a
server id, e.g. `mcp__<id>__generate_image`).

## 0. Ask before spending MCP credits — check for Unlimited first

Do this before anything else in this doc, every time, not just once per
project. The provider's "Unlimited" access (a paid, per-model, often
365-day pass that makes generations on that model free) is honored **only
on the provider's own website — never through MCP.** MCP always charges
standard credits, regardless of what the account owns. This isn't a
guess — it was confirmed directly on a real Higgsfield account: GPT Image
was on an active 365-day Unlimited pass in account settings the whole time,
and every MCP call for it still billed credits at the normal rate. The
account's `balance`/`show_plans_and_credits` MCP tools don't even see it —
they reported `unlim.available: false` while the account's own website
settings page showed 8 models actively Unlimited. MCP has no visibility
into it and no way to spend against it; from MCP's side it simply isn't
there.

So, before calling `generate_image`/`generate_video` for a new asset:

1. **Ask the user** whether the model you're about to use is one they have
   Unlimited on (or check yourself, if you have access to their logged-in
   browser session: their account's Settings → Subscription page lists
   active Unlimited models with expiry dates).
2. **If it's covered**, the cheaper path is generating it on the website
   instead — either the user does it manually and hands you the finished
   files to drop into `assets/`, or you drive their logged-in browser
   session to do it. Either way, no MCP call, no credits spent.
3. **Reserve direct MCP `generate_image`/`generate_video` calls** for what
   actually needs them: models outside the user's Unlimited coverage
   (video models in particular are rarely covered — check, don't assume),
   and anything that genuinely requires scripting — a multi-shot
   consistency chain passing one image's job_id as a reference into nine
   more prompts, batch generation, anything unattended. That kind of
   chaining isn't practical to reproduce by hand on the website, so MCP is
   the right tool for it even when the model itself happens to be
   Unlimited.

Don't treat this as a one-time setup question — ask again for each new
project/session, since Unlimited passes expire (some are only 7 days) and
the set of covered models changes over time.

## 0b. The hybrid that actually works: generate on the website, read over MCP

When the images are covered by Unlimited but the video is not, you do not have
to choose one channel. Generate the stills on the website (free), then call
`show_generations(type:"image")` over MCP — it returns each generation's `id`,
its full prompt, and a public `results.rawUrl` on the provider's CDN. That
gives you both halves you need:

- `curl` the `rawUrl` to pull the file down locally for ffmpeg, and
- pass the generation `id` straight into a paid MCP `generate_video` call as a
  `medias[].value` (role `start_image` / `end_image` / `image_references`).

So website-generated stills can seed MCP video jobs without any upload step.
Confirmed on a real Higgsfield account: website generations came back with
`use_unlim: true` in their params (no credits spent) and their ids worked as
video keyframes. Poll `show_generations` after each submit — the website UI
and this listing lag each other by a few seconds in both directions, so a job
still showing "Processing" on screen may already be listed as completed, and
vice versa.

Two UI facts worth not rediscovering:

- **Attach a reference by hovering the image in the gallery and clicking
  "Reference"** — that path is reliable. Uploading a file into the prompt
  bar's file input hangs at "Processing" indefinitely on some accounts; the
  job never lands in `show_generations` at all.
- The hover toolbar belongs to *whichever image the cursor is over*, so a
  mis-aimed click attaches the wrong reference silently. Verify the thumbnail
  in the prompt bar before generating, and remove a wrong one by clicking the
  small × at its top-right corner.
- A page reload clears the Unlimited toggle back to off. Re-check it, or the
  next generation quietly costs credits.

## 1. Resolve named models before generating anything

Design briefs often name a specific model ("GPT Image 2", "Seedance 4K").
Don't assume the id — search first:

```
models_explore(action:"search", query:"GPT Image", type:"image")
models_explore(action:"search", query:"Seedance", type:"video")
```

An exact name match (e.g. `gpt_image_2`) is safe to use directly. If nothing
matches exactly (e.g. "Seedance 4K" doesn't exist but `seedance_2_0` supports
`resolution:"4k"` in `mode:"std"`), that's a judgment call for the user, not
you — ask which fallback they want rather than silently substituting,
especially before spending real generation credits on a 10-asset run.

## 2. Preflight cost on anything you're about to run many times

```
generate_image(params:{..., get_cost:true})   # no job submitted, just a credit quote
generate_video(params:{..., get_cost:true})
```

Multiply by however many you're about to generate and mention the total to
the user before running a batch — video generation in particular can be an
order of magnitude more expensive than images (observed: ~7 credits for a 2K
image vs. ~330 credits for a 15s/4K video). Check `balance()` too; don't
assume the number reported by `get_cost` alone tells you if the run is
affordable.

## 3. Generate one anchor, then reference it everywhere else

For visual consistency across a set of shots of "the same" subject (same
building, same product, same character), generate the primary/hero shot
alone first, then pass its `job_id` as a `medias` entry with role `"image"`
(the exact role name varies by model — check `models_explore(action:"get",
model_id:...)` for the roles a model accepts) on every subsequent prompt:

```
medias: [{ value: "<hero-job-id>", role: "image" }]
```

This is far more reliable for "same cabin / same product / same character
across 10 images" than describing the subject in words each time.

## 4. Expect a low concurrency ceiling, not a credit-exhaustion error

`generate_image_batch` submitting >2-3 jobs at once can return
`"Out of credits on plus (monthly) plan"` or `"Not enough boost credits"` for
some items even when `balance()` shows plenty of credits remaining. This was
observed to be a **concurrency limit** (roughly 2 simultaneous jobs on a Plus
plan), not real exhaustion. Recovery:

1. Call `balance()` to confirm credits are actually fine.
2. Resubmit the failed indices in smaller batches (pairs work reliably),
   waiting for each pair to reach a terminal state via `jobs_wait` before
   submitting the next pair.

Don't burn retries assuming the account is out of money — check first.

## 5. Poll, don't sleep-loop

`jobs_wait` is a long-poll (max ~15s per call). Call it repeatedly until
`all_terminal` is true rather than writing your own sleep/retry loop — video
generation at high resolution can take several minutes, so expect to call it
many times in a row for a single video job. That's normal, not a hang.

## 6. Download and compress — never ship the raw generation output

Generation results come back as a `result_url` (often a large PNG or an
HEVC-codec MP4 straight from the model). Download locally, then:

```bash
# Images: cap width, moderate JPEG quality
ffmpeg -y -i in.png -vf "scale='min(1800,iw)':-2" -q:v 4 out.jpg

# Video: re-encode to H.264 (HEVC has poor <video>-tag support), strip audio
# if unused, and use DENSE keyframes if the video will be scroll-scrubbed
# (seeking needs a keyframe near every target time or it looks jumpy/laggy)
ffmpeg -y -i in.mp4 \
  -vf "scale=1920:1080:flags=lanczos" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -g 12 -keyint_min 12 -sc_threshold 0 \
  -movflags +faststart -an \
  out.mp4

# Poster frame for the video (shows instantly, before the video itself loads)
ffmpeg -y -i out.mp4 -vf "select=eq(n\,0)" -vframes 1 -q:v 3 poster.jpg
```

A 15s/4K source typically re-encodes down to ~15-20MB at 1080p, which is
still large for a "single page" — that's expected for a hero video and is
why assets live in an external `assets/` folder rather than being inlined as
base64 (see the main SKILL.md).
