# Reusable page patterns

Copy-adapt these rather than reinventing them each time.

## Fluid type with clamp()

```css
:root{
  --display: 'Darker Grotesque', sans-serif;  /* swap for the brief's fonts */
  --body: 'Hanken Grotesk', sans-serif;
}
h1{ font-size: clamp(2.2rem, 5.4vw, 4.2rem); }   /* min, viewport-scaled, max */
```

`clamp()` beats separate `@media` font-size rules for headline-style text —
it scales continuously instead of jumping at breakpoints. Reserve `@media`
for structural changes (columns, nav visibility, padding), not type size.

**Watch out**: if a brand wordmark or oversized display text gets a long
string (e.g. a brand rename from "Vesper" to "MG Webdesigner"), a clamp tuned
for the short string will overflow badly at the same viewport-width
percentage. Re-tune the `vw` coefficient proportionally to the new string
length, don't just leave it.

## Nav that solidifies on scroll

```css
.nav{ position:fixed; top:0; left:0; right:0; z-index:100;
  background:transparent; transition:background .4s ease, padding .4s ease; }
.nav.solid{ background:rgba(10,20,20,.86); backdrop-filter:blur(14px); }
```
```js
window.addEventListener('scroll', function(){
  nav.classList.toggle('solid', window.scrollY > 40);
}, {passive:true});
```

## Scroll-reveal without a library

```css
.reveal{ opacity:0; transform:translateY(28px); transition:opacity .8s ease, transform .8s ease; }
.reveal.in{ opacity:1; transform:translateY(0); }
```
```js
var io = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
  });
}, {threshold:.15});
document.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });
```

## Guaranteed hero background (don't rely on JS alone)

Any hero built from a `<video>` that only appears once JS toggles an
`is-active` class after `loadedmetadata` can render as a blank/dark section
if that event is delayed (slow network, mobile data-saver, autoplay policy).
Give the container a plain CSS background image as a floor that always
renders:

```css
.hero-sticky{
  background: url('assets/images/hero-poster.jpg') center/cover no-repeat;
}
```

The video then plays *on top of* a real photo instead of on top of nothing.
Also mark the first video layer `is-active` directly in the HTML (not only
via JS) so its `opacity:1` and `poster` attribute show immediately:

```html
<video class="hero-video is-active" poster="assets/images/hero-poster.jpg" ...>
```

## Booking / pricing calculator pattern

The recurring shape: two date inputs, a guest/quantity stepper, a computed
breakdown, and a minimum-threshold validation message. Core logic (adapt
field names/rate/minimum):

```js
var RATE = 540, FEE = 180, MIN_NIGHTS = 2;

function nightsBetween(inIso, outIso){
  var a = new Date(inIso + 'T00:00:00');
  var b = new Date(outIso + 'T00:00:00');
  return Math.round((b - a) / 86400000);
}

function recalc(){
  if(!checkin.value || !checkout.value){ breakdown.style.display='none'; return; }
  var nights = nightsBetween(checkin.value, checkout.value);
  if(nights < MIN_NIGHTS){
    errorBox.classList.add('show');
    breakdown.style.display = 'none';
    return;
  }
  errorBox.classList.remove('show');
  breakdown.style.display = 'grid';
  var subtotal = nights * RATE;
  totalEl.textContent = fmt(subtotal + FEE);
}
checkin.addEventListener('change', recalc);
checkout.addEventListener('change', recalc);
```

Also set `checkin.min = today` and update `checkout.min = checkin.value + 1
day` on change, so the native date pickers can't select an impossible range
in the first place — validate both at the input level *and* in `recalc()`
(a user can still type/paste an invalid pair).

**Test this for real, not just visually.** Set both date fields via
`form_input`/`javascript_tool`, then explicitly `dispatchEvent(new
Event('change'))` on them (`form_input` alone does not reliably fire
`change` in headless browser tools), then read the computed totals back out
and check the arithmetic — once for a valid multi-night stay, once for a
below-minimum stay to confirm the error path.
