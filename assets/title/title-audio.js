// Entrance sounds follow the CSS animation events, so slow asset loading cannot
// start them before the artwork. The supplied clips contain short sounds followed
// by silence; retain the original recordings and stop playback on skip or start.
(() => {
  const title = document.getElementById('title');
  const character = document.getElementById('character-entrance-sound');
  const ghost = document.getElementById('ghost-entrance-sound');
  const logo = document.getElementById('logo-move-sound');
  const landing = document.getElementById('logo-land-sound');
  const readyVoice = document.getElementById('title-ready-voice');
  const selection = document.getElementById('start-select-sound');
  const menuChange = document.getElementById('menu-change-sound');
  const music = document.getElementById('title-music');
  const entranceSounds = [character, ghost, logo, landing];
  const sounds = [...entranceSounds, readyVoice, selection, menuChange, music];
  let impactTimer, voicePlayed = false;
  sounds.forEach(sound => { sound.volume = 0.7; });
  readyVoice.volume = 0.8;
  music.volume = 0.3;
  readyVoice.addEventListener('ended', () => { music.volume = 0.45; });

  function stopSounds() {
    clearTimeout(impactTimer);
    sounds.forEach(sound => {
      sound.pause();
      sound.currentTime = 0;
    });
  }

  function play(sound) {
    sound.currentTime = 0;
    sound.dataset.cueAt = String(performance.now());
    sound.play().then(() => {
      sound.dataset.playback = 'played';
      if (sound === music) hint(false);
    }).catch(error => {
      sound.dataset.playback = error.name === 'NotAllowedError' ? 'blocked' : 'error';
      // Browsers block autoplay on a site the visitor has not interacted with yet: start the theme on the first click or key.
      if (sound === music && error.name === 'NotAllowedError') armResume();
    });
  }
  let resumeArmed = false;
  function hint(show) { const h = document.getElementById('sound-hint'); if (h) h.hidden = !show; }
  function armResume() {
    if (resumeArmed) return; resumeArmed = true; hint(true);
    const resume = () => { document.removeEventListener('pointerdown', resume, true); document.removeEventListener('keydown', resume, true);
      if (!title.hidden && !title.classList.contains('confirming')) play(music); hint(false); };
    document.addEventListener('pointerdown', resume, true); document.addEventListener('keydown', resume, true);
  }

  title.addEventListener('animationstart', event => {
    if (title.hidden || document.hidden || !title.classList.contains('opening')) return;
    if (event.animationName === 'hero-tumble' && event.target.classList.contains('heroine-entry')) {
      play(character);
    }
    if (event.animationName === 'ghost-swoop' && event.target.classList.contains('ghost-entry')) {
      play(ghost);
    }
    if (event.animationName === 'title-impact' && event.target.classList.contains('logo-entry')) {
      play(logo);
      // The logo first lands at 42% of its 850 ms entrance animation.
      impactTimer = setTimeout(() => {
        if (title.classList.contains('opening') && !title.hidden && !document.hidden) {
          title.dispatchEvent(new Event('titleimpact'));
        }
      }, 357);
    }
  });
  function startTitleTheme() {
    if (!voicePlayed && !title.hidden && !document.hidden && !title.classList.contains('confirming')) {
      voicePlayed = true;
      title.classList.add('title-celebration');
      play(music);
      play(readyVoice);
    }
  }
  title.addEventListener('titleimpact', () => {
    play(landing);
    startTitleTheme();
  });
  title.addEventListener('introready', () => {
    clearTimeout(impactTimer);
    entranceSounds.forEach(sound => { sound.pause(); sound.currentTime = 0; });
    // Skipping the entrance or using reduced motion still starts the title theme.
    startTitleTheme();
  });
  title.addEventListener('startconfirm', () => {
    stopSounds();
    play(selection);
  });
  title.addEventListener('menuchange', () => play(menuChange));
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stopSounds();
  });
})();
