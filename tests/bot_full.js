const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('error',e=>console.log('PAGE CRASH',e.message)); p.on('framenavigated',f=>console.log('NAVIGATED',f.url()));
await p.setViewport({width:1029,height:700}); await p.goto('http://127.0.0.1:8000/index.html?bot=1'); await new Promise(r=>setTimeout(r,12000));
let last='', t0=Date.now(); const log=[];
while((Date.now()-t0)/1000<1500){ await new Promise(r=>setTimeout(r,2000));
  const s=await p.evaluate(()=>({lvl:level,alive:candles.filter(c=>c.state==='alive').length,crates:crates.flat().filter(v=>v>0).length,lives,time:Math.ceil(timeLeft/60),score,bombCap,RANGE,spd:hero.speed,win:winT>0,clear:cleared,over:gameOver,escaped,stuck:botState.stuck}));
  const key=JSON.stringify([s.lvl,s.alive,s.lives,s.win,s.clear,s.over,s.escaped]);
  if(key!==last){ const line=((Date.now()-t0)/1000).toFixed(0)+'s '+JSON.stringify(s); console.log(line); log.push(line); last=key; }
  if(s.clear && !s.escaped){ await p.keyboard.press('Space'); await new Promise(r=>setTimeout(r,6500)); }
  if(s.escaped||s.over){ await p.screenshot({path:'tests/out/bot_full_end.png'}); break; } }
console.log('errors',errs); await b.close();})();
