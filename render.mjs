#!/usr/bin/env node
// Render a video HTML file to MP4 (or a few stills) deterministically.
//
//   node render.mjs videos/hello.html             -> out/hello.mp4
//   node render.mjs videos/hello.html --stills 3  -> out/hello-still-1.png ... -3.png
//   node render.mjs videos/hello.html --still 4 --scale 2 -> out/hello-still.png (one frame at t=4s, 2x pixels)
//   options: --fps 30 (default 30), --scale N (pixel density, default 1)
//
// A video page must define window.DURATION (seconds), window.SIZE ([w, h])
// and window.render(t), which draws the exact frame for time t in seconds.

import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

// createRequire finds Playwright in a local node_modules or via NODE_PATH.
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

function parseArgs(argv) {
  const opts = { input: null, fps: 30, stills: 0, still: null, scale: 1 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--stills") opts.stills = parseInt(argv[++i] ?? "3", 10);
    else if (a === "--fps") opts.fps = parseInt(argv[++i], 10);
    else if (a === "--still") opts.still = parseFloat(argv[++i]);
    else if (a === "--scale") opts.scale = parseFloat(argv[++i]);
    else if (!opts.input) opts.input = a;
    else throw new Error(`Unexpected argument: ${a}`);
  }
  if (!opts.input) {
    console.error("Usage: node render.mjs videos/<name>.html [--stills N | --still SECONDS] [--scale N] [--fps 30]");
    process.exit(1);
  }
  if (opts.still !== null && !(opts.still >= 0)) throw new Error("--still needs a time in seconds");
  if (!(opts.scale > 0)) throw new Error("--scale must be a positive number");
  if (!(opts.fps > 0)) throw new Error("--fps must be a positive number");
  if (Number.isNaN(opts.stills) || opts.stills < 0) throw new Error("--stills must be a positive number");
  return opts;
}

const opts = parseArgs(process.argv.slice(2));
const inputPath = path.resolve(opts.input);
const name = path.basename(inputPath, path.extname(inputPath));
const outDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), "out");
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
try {
  // Read the size first with a throwaway page, then open at the exact size.
  const probe = await browser.newPage();
  await probe.goto(pathToFileURL(inputPath).href);
  const [width, height] = await probe.evaluate(() => window.SIZE ?? [1920, 1080]);
  await probe.close();

  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: opts.scale });
  page.on("pageerror", (e) => console.error("Page error:", e.message));
  await page.goto(pathToFileURL(inputPath).href);
  // Kill any CSS animations/transitions so only render(t) moves things.
  await page.addStyleTag({
    content: "*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}",
  });
  await page.evaluate(() => document.fonts.ready);

  const { duration, hasRender } = await page.evaluate(() => ({
    duration: window.DURATION,
    hasRender: typeof window.render === "function",
  }));
  if (!hasRender) throw new Error("The video must define window.render(t).");
  if (!(duration > 0)) throw new Error("The video must set window.DURATION to a number of seconds.");

  const totalFrames = Math.round(duration * opts.fps);

  const frameAt = async (t) => {
    await page.evaluate(async (t) => {
      await window.render(t);
      // Wait for layout + paint of this frame.
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    }, t);
    return page.screenshot({ type: "png", clip: { x: 0, y: 0, width, height } });
  };

  if (opts.still !== null) {
    const { writeFileSync } = await import("node:fs");
    const t = Math.min(opts.still, duration);
    const file = path.join(outDir, `${name}-still.png`);
    writeFileSync(file, await frameAt(t));
    console.log(`Still at t=${t}s (${width * opts.scale}x${height * opts.scale}) -> ${path.relative(process.cwd(), file)}`);
  } else if (opts.stills > 0) {
    const { writeFileSync } = await import("node:fs");
    const n = opts.stills;
    for (let i = 0; i < n; i++) {
      // Evenly spaced from the first frame to the last frame.
      const frame = n === 1 ? Math.floor(totalFrames / 2) : Math.round((i * (totalFrames - 1)) / (n - 1));
      const t = frame / opts.fps;
      const file = path.join(outDir, `${name}-still-${i + 1}.png`);
      writeFileSync(file, await frameAt(t));
      console.log(`Still ${i + 1}/${n} at t=${t.toFixed(2)}s -> ${path.relative(process.cwd(), file)}`);
    }
  } else {
    const outFile = path.join(outDir, `${name}.mp4`);
    // Even dimensions are required for yuv420p.
    const ff = spawn("ffmpeg", [
      "-y", "-loglevel", "error",
      "-f", "image2pipe", "-framerate", String(opts.fps), "-c:v", "png", "-i", "-",
      "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
      "-c:v", "libx264", "-preset", "medium", "-crf", "18",
      "-pix_fmt", "yuv420p", "-r", String(opts.fps), "-movflags", "+faststart",
      outFile,
    ], { stdio: ["pipe", "inherit", "inherit"] });
    const done = new Promise((resolve, reject) => {
      ff.on("error", reject);
      ff.on("close", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg exited with ${code}`))));
    });

    for (let f = 0; f < totalFrames; f++) {
      const png = await frameAt(f / opts.fps);
      if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once("drain", r));
      if (f % opts.fps === 0 || f === totalFrames - 1) {
        process.stdout.write(`\rFrame ${f + 1}/${totalFrames}`);
      }
    }
    ff.stdin.end();
    await done;
    console.log(`\nWrote ${path.relative(process.cwd(), outFile)} (${width}x${height}, ${opts.fps} fps, ${duration}s)`);
  }
} finally {
  await browser.close();
}
