# Motion Studio

Motion graphics written as code. Each video is one HTML file; every frame is a pure function of time, so renders are identical every time.

## Make a video

Create `videos/<name>.html` that links `../brand.css` and sets:

```js
window.DURATION = 3;            // seconds
window.SIZE = [1920, 1080];     // [width, height] in pixels
window.render = (t) => { ... }; // draw the exact frame at time t (seconds)
```

No CSS animations, transitions, timers or `requestAnimationFrame` loops: all motion comes from `render(t)`. See `videos/hello.html`.

## Render

```bash
node render.mjs videos/hello.html            # -> out/hello.mp4 (30 fps, H.264)
node render.mjs videos/hello.html --stills 3 # -> out/hello-still-1..3.png (quick check, not committed)
node render.mjs videos/hello.html --still 4 --scale 2 # -> out/hello-still.png, one 2x frame at t=4s
```

Needs Node 18+, ffmpeg, and Playwright with Chromium (`npm install && npx playwright install chromium`).

## Brand: Be Made Whole™ (Clyde Lewis)

`brand.css` holds the official brand tokens. Use the variables, never raw values:

| Variable | Role | Hex |
|---|---|---|
| `--royal-blue` / `--bg` | Background | `#123F70` |
| `--warm-gold` / `--accent` | Accent | `#FFDF62` |
| `--soft-ivory` / `--text` | Text | `#F8F6EF` |
| `--muted-blue` / `--muted` | Muted | `#A9B9C9` |

Fonts: Lato 900 for headlines (`--font-headline`, `.headline`) and Lato 400 for body (`--font-body`, `.body`), loaded from `fonts/` so renders work offline. Lato is licensed under the SIL Open Font License (`fonts/OFL.txt`). Helper classes: `.headline`, `.body`, `.label`, `.author`.

`videos/brand-check.html` is the reference layout.
