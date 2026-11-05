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
node render.mjs videos/hello.html --stills 3 # -> out/hello-still-1..3.png
```

Needs Node 18+, ffmpeg, and Playwright with Chromium (`npm install && npx playwright install chromium`).

Colors and fonts live in `brand.css`.
