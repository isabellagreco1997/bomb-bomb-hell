// Draw authored frame sequences without moving or rescaling the complete sprite.
// Kept separate from the entrance choreography in title.js/title.css.
(() => {
  const title = document.getElementById('title');
  if (!title) return;
  const stages = [...title.querySelectorAll('canvas[data-title-sprite]')];
  if (!stages.length) return;
  let tracks = [], frameRequest = 0, epoch = performance.now(), previousTick = -1, playbackFps = 12;
  const ready = fetch('assets/title/sprites/manifest-grid250.json')
    .then(response => {
      if (!response.ok) throw new Error('Title sprite manifest unavailable');
      return response.json();
    })
    .then(async manifest => {
      tracks = await Promise.all(stages.map(async canvas => {
        const definition = manifest.sprites[canvas.dataset.titleSprite];
        const atlas = new Image();
        atlas.src = 'assets/title/sprites/' + definition.file;
        await atlas.decode();
        const nativeStage = definition.stage || manifest.stage;
        canvas.width = nativeStage[0];
        canvas.height = nativeStage[1];
        canvas.dataset.atlas = definition.file;
        const context = canvas.getContext('2d');
        context.imageSmoothingEnabled = false;
        const floatingPieces = await Promise.all((definition.floatingPieces || []).map(async piece => {
          const image = new Image();
          image.src = 'assets/title/sprites/' + piece.file;
          await image.decode();
          return { ...piece, image };
        }));
        return { canvas, context, atlas, definition, floatingPieces };
      }));
      playbackFps = Math.max(...tracks.map(track => track.definition.fps));
      draw(0, true);
      title.classList.add('sprites-ready');
      frameRequest = requestAnimationFrame(frame);
    }).catch(error => {
      // Static original images stay visible if a sprite atlas cannot load.
      title.dataset.spriteStatus = 'fallback';
      console.warn(error.message);
    });
  window.titleSpritesReady = ready;
  function draw(seconds, still) {
    for (const { canvas, context, atlas, definition: d, floatingPieces } of tracks) {
      const cycle = d.playback === 'ping-pong' ? Math.max(1, 2 * d.frames - 2) : d.frames;
      const step = still ? 0 : Math.floor(seconds * d.fps) % cycle;
      const index = step < d.frames ? step : cycle - step;
      const sx = (index % d.columns) * d.size[0];
      const sy = Math.floor(index / d.columns) * d.size[1];
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(atlas, sx, sy, d.size[0], d.size[1], d.origin[0], d.origin[1], d.size[0], d.size[1]);
      const piecePositions = [];
      for (const piece of floatingPieces) {
        const time = still ? 0 : seconds;
        const bob = Math.round(piece.amplitude * Math.sin(time * 2 * Math.PI / piece.period + piece.phase));
        const x = piece.origin[0], y = piece.origin[1] + bob;
        context.drawImage(piece.image, x, y);
        piecePositions.push([x, y]);
      }
      if (floatingPieces.length) canvas.dataset.floatingPositions = JSON.stringify(piecePositions);
      canvas.dataset.frame = String(index);
    }
  }
  function frame(now) {
    frameRequest = 0;
    if (title.hidden || document.hidden) return;
    const still = title.classList.contains('still');
    const seconds = (now - epoch) / 1000;
    const tick = still ? -2 : Math.floor(seconds * playbackFps);
    if (tick !== previousTick) {
      draw(seconds, still);
      previousTick = tick;
    }
    frameRequest = requestAnimationFrame(frame);
  }
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && !title.hidden && !frameRequest && tracks.length) {
      epoch = performance.now(); previousTick = -1;
      frameRequest = requestAnimationFrame(frame);
    }
  });
  title.addEventListener('introreplay', () => { epoch = performance.now(); previousTick = -1; });
})();
