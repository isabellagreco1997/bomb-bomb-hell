# Bomb Bomb Hell! layered title

The title uses the original artwork from **Create Hazbin Bomberman assets**, converted to a shared 350 × 280 logical pixel stage (four source pixels per logical pixel). Source PNGs remain untouched in this folder. The heroine is the original-horns revision, preserving the approved face, pose, horns and clothing.

## Artwork and sprite animation

`tools/build_title_sprites.py` cleans detached edge noise and pale matte remnants, creates binary transparency, and reduces the palette without dithering. It builds the derived artwork and sprite atlases in `sprites/`.

Animation artwork is stored separately in `sprites/keyframes/`:

- Heroine: 8 authored pixel-map key poses with redrawn trailing hair contours, upper-eyelid poses and fuse sparks. The body, face outside the eyelids, horns, clothing and limbs stay registered.
- Ghost: 6 key poses with newly drawn flame silhouettes/hot cores and a small eyelid change. The wax body stays fixed.
- Logo: 4 key poses with drawn fuse sparks and border-jewel highlights. Lettering and the overall silhouette stay fixed.

`pixel-art.json` records the original palette and each explicitly drawn pixel row. Spaces erase a pixel; dots retain it. The source keyframe PNGs are the artwork. `tools/build_title_sprites.py` only cleans the static base art, places the existing keyframes and packs a 60-step, five-second timeline at 12 fps. It no longer invents motion by warping source regions.

The work follows [Sprite Forge](https://github.com/isabellagreco1997/sprite-forge): inspect a numbered pixel map and parts preview, keep fixed parts unchanged, preserve the source palette, and inspect frames and loops at enlarged and native scales. The original art is retained; rejected generated sheets were not integrated.

`sprite-player.js` plays the packed frames with nearest-neighbor scaling. Motion Off freezes frame zero; hidden titles/tabs stop drawing. Static corrected sprites provide a loading-error fallback. All artwork, including skyline and menu, shares one displayed pixel grid.

## Opening and controls

`title.css` choreographs the 4.2-second entrance: skyline at 0s, heroine at 0.4s, ghost at 1s, fuse glint at 1.65s, logo at 2.15s, menu at 3.05s and start prompt at 3.65s. The sprite animation continues within these entrance layers.

`title.js` handles image readiness, mouse/keyboard input, instructions, Skip Intro, Replay Intro and reduced motion. Up/down selects; Enter/Space activates. During the opening, Enter/Space/Escape skip to the menu. Motion Off freezes frame zero and disables replay. The entrance waits for artwork decoding before starting.

Play transitions to the existing game in `demo.html`. The title is silent pending the selected song; existing gameplay audio remains in place. Original video assets are retained but not loaded.

## Validation

Run `python3 tools/check_title_sprites.py` for atlas dimensions, binary alpha, frame changes and fixed-body assertions. JavaScript syntax and whitespace checks also pass. Chrome verification covers loaded/advancing sprite canvases, Motion Off freezing frame zero, replay/skip, and successful transition into the game without visible runtime errors.
