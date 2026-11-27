# ContentSkills projects

Source for videos made with [ContentSkills](https://github.com/blotato/contentskills). The rendered videos are in `../out/`.

- `never-afraid/`: "You were never meant to live afraid" (`out/never-afraid.mp4`). Script, the storyboard generator and its output.
- `contentskills-fixes.patch`: two small fixes to ContentSkills that this video needs: a `speed` option on shot pieces, so a title lands inside a short shot, and a temp-folder cleanup that retries instead of crashing the build.

To rebuild: set up ContentSkills, apply the patch in its folder (`git apply contentskills-fixes.patch`), copy `never-afraid/` to `projects/never-afraid/`, then `node projects/never-afraid/build-storyboard.mjs`, mark the picks and run `npm run make never-afraid -- --scale 1`.
