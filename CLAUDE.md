# Bomb Bomb Hell! — briefing for an AI agent

You are working on a finished, playable browser game. Read this before touching anything.

## Layout

- `index.html` — the whole game in one inline script. Sections in order: level table and state, world (tiles, crates, exit, power-up), entities (hero, ghosts, bombs, fires, flames), the bot, `update()` at a fixed 60 Hz, `draw()` once per frame, the title hand-off. The game loop is time-based: never tie speed to frame count.
- `assets/atlas.png` + `assets/atlas.json` — every sprite frame, packed by `tools/atlas.py`. Frames have mixed sizes; `drawFrame()` bottom-anchors a frame on its tile and centres it horizontally. After adding or renaming a frame, run `python3 tools/atlas.py`.
- `assets/sprites/48/anim/` — the frames themselves. Naming: `heroine_idle_<dir>_N`, `heroine_cycle_<dir>_N` (walk), `heroine_start_N`, `heroine_death_N`, `heroine_win_N`, `ghost_flicker_N` (idle/wander), `ghost_hurt_N`, `ghost_defeated_N`, `ghost_spit_N`, `flame_N`, `bomb_tick_N`, `fire_h/v/c_N`, `tile_*`, `pw_*`, `hud_*`.
- `assets/audio/` — `voice_*.mp3` sets with a matching `voice_*.json` list, `sfx_*.mp3` effects, `music_*.mp3`. Raw recordings in `assets/audio/src/`. Voice lines are played through `pickPlay(set, last)`: one voice channel, a new line interrupts the current one, never the same line twice running.
- `assets/title/` — the title screen (layered pixel scene, menu, its own sounds and font). It hands over to the game by calling `showGame()` after `#play` is activated.
- `assets/src/` — the generated sheets and reference material the sprites were cut from.
- `tools/` — the asset pipeline (Python: Pillow, numpy, scipy; ffmpeg on PATH). `spritecut.py` has the shared helpers: `key()` (background keying), `largest_blob()` (keeps the main shape and fills enclosed holes), `fit()` (premultiplied downscale), `quantise()` (shared palette).

## Rules we learned the hard way

1. Generated sprite sheets are concept art, not sprites: thousands of colours, no grid, "walk cycles" that do not step. Cut, key, downscale with a premultiplied resize, quantise to a shared palette. Verify at zoom on the game's floor colour, not on white.
2. Real animation comes from generated video of the character walking on the spot, one direction per clip. Measure before sampling: frame-to-frame difference (drop held duplicates), the leg-spread or foot-height signal for the cycle period, hair width to match scale between clips. Anchor standing poses by the head, falls by the floor.
3. Never puppet a sprite by offsetting body parts; seams read as cuts. Lock what does not move, take motion from the footage, mirror a clean half onto a smeared one half a cycle later if you must.
4. Dark pixels near the background colour get keyed out: eyes, bomb spheres, flame cores. Fill enclosed holes; for static objects build one mask from an unlit frame.
5. Idle is secondary motion only: hair, sleeves, a blink. Never bob the whole body.
6. An animation change is verified with a screenshot or a headless test, never by reading the code. Assert every text edit landed; a `//` comment appended to a line can swallow the rest of the line.
7. One voice channel. Sounds start with the animation they belong to.
8. Frame rate is not time. Browsers halve `requestAnimationFrame` on low battery.

## Testing

- `tests/` drives headless Chrome with puppeteer-core (`npm install`, set `CHROME` to your Chrome binary if it is not in /Applications): `npm test` runs smoke, keys, enemy and spit checks; `npm run test:levels` cheats through the level flow; `npm run bot` lets the bot play a full game (15 to 20 minutes) and prints where the balance breaks. Serve the game on port 8000 first (`npm run serve`).
- `?showcase=1` runs a scripted round through every sound with captions. `?bot=1` plays the game by itself; a full run takes 15 to 20 minutes and reports where the balance breaks.
- Serve locally (`npm run serve`); the atlas will not load from `file://`.

## Extending

- New enemy: cut frames into `assets/sprites/48/anim/` with a clear prefix, add the names and an `anims` entry in `tools/atlas.py`, add a spawn and a behaviour block in `update()`, a draw block in `draw()`, and a danger rule in `dangerMap()` so the bot can dodge it.
- New level: add a row to `LEVELS` (size, enemies, crate rate, enemy speed, power-up, time, spit cooldown).
- New sound: drop the file in `assets/audio/` with the `voice_`/`sfx_`/`music_` prefix; for a voice set run `tools/cut_audio.py <file> <set> 1.3` to split one recording into lines and build the list.
