(() => {
  const title=document.getElementById('title');
  const buttons=[...document.querySelectorAll('.menu-item')];
  const help=document.getElementById('howtoplay');
  const preference=matchMedia('(prefers-reduced-motion: reduce)');
  const INTRO_DURATION=4200;
  // Keep the background and typography at an integer display scale.
  // Detailed sprite tracks retain their native resolution and individual layout.
  const stage=document.getElementById('titlebox');
  const fitMenu=()=>{
    const scale=Math.max(1,Math.floor(Math.min(title.clientWidth/250,title.clientHeight/200)));
    const width=250*scale,height=200*scale;
    title.style.setProperty('--ui-pixel',`${scale}px`);
    Object.assign(stage.style,{
      width:`${width}px`,height:`${height}px`,
      left:`${Math.floor((title.clientWidth-width)/2)}px`,
      top:`${Math.floor((title.clientHeight-height)/2)}px`
    });
  };
  fitMenu();
  new ResizeObserver(fitMenu).observe(title);
  let selected=0, opening=false, loaded=false, introTimer;
  function select(index,focus=false){
    if(playing) return;
    const previous=selected;
    selected=(index+buttons.length)%buttons.length;
    buttons.forEach((button,i)=>button.classList.toggle('selected',i===selected));
    if(selected!==previous&&loaded&&!opening&&!title.hidden) title.dispatchEvent(new Event('menuchange'));
    if(focus) buttons[selected].focus({preventScroll:true});
  }
  function finishIntro(focus=false){
    if(playing) return;
    clearTimeout(introTimer);
    opening=false;
    title.classList.remove('loading','opening');
    buttons.forEach(button=>button.disabled=false);
    if(focus) select(0,true);
    title.dispatchEvent(new Event('introready'));
  }
  function playIntro(){
    if(!loaded||playing) return;
    if(title.classList.contains('still')){ finishIntro(); return; }
    clearTimeout(introTimer);
    title.classList.remove('opening','loading');
    // Start the entrance timeline after the artwork has loaded.
    void title.offsetWidth;
    opening=true;
    buttons.forEach(button=>button.disabled=true);
    title.classList.add('opening');
    title.dispatchEvent(new Event('introreplay'));
    introTimer=setTimeout(()=>finishIntro(),INTRO_DURATION);
  }
  function setMotion(enabled){
    title.classList.toggle('still',!enabled);
    title.classList.toggle('motion-enabled',enabled);
    if(loaded&&!enabled) finishIntro();
  }
  setMotion(!preference.matches);
  preference.addEventListener('change',event=>setMotion(!event.matches));
  buttons.forEach((button,i)=>{
    button.addEventListener('pointerenter',()=>select(i));
    button.addEventListener('focus',()=>select(i));
  });
  document.getElementById('play').addEventListener('click',startFromTitle);
  document.getElementById('instructions').addEventListener('click',()=>help.showModal());
  document.getElementById('close-help').addEventListener('click',()=>help.close());
  help.addEventListener('close',()=>document.getElementById('instructions').focus());
  document.addEventListener('keydown',event=>{
    if(title.hidden||playing||help.open||!loaded||event.altKey||event.ctrlKey||event.metaKey) return;
    if(opening){
      if(['Enter',' ','Escape'].includes(event.key)){
        event.preventDefault();
        if(!event.repeat) finishIntro(true);
      }
      return;
    }
    if(['ArrowUp','ArrowDown','Enter',' '].includes(event.key)){
      event.preventDefault();
      if(event.repeat) return;
      if(event.key==='ArrowUp') select(selected-1,true);
      else if(event.key==='ArrowDown') select(selected+1,true);
      else buttons[selected].click();
    }
  });
  // Decode first so a slow image load cannot miss its entrance cue.
  Promise.allSettled([...title.querySelectorAll('img')].map(img=>img.decode()).concat(window.titleSpritesReady || Promise.resolve(),document.fonts.load('16px HellMenuPixel'))).then(()=>{
    loaded=true;
    playIntro();
  });
})();
