const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.setViewport({width:1029,height:700}); await p.goto('http://127.0.0.1:8000/index.html'); await new Promise(r=>setTimeout(r,6000)); await p.click('#play'); await new Promise(r=>setTimeout(r,7000));
// power-up pickup
await p.evaluate(()=>{ crates[powerTile.y][powerTile.x]=0; hero.x=powerTile.x; hero.y=powerTile.y; hero.px=hero.x*T; hero.py=hero.y*T; }); await new Promise(r=>setTimeout(r,300));
const pu=await p.evaluate(()=>({taken:powerTile.taken,bombCap,RANGE,score}));
// timer runs out -> 3 more enemies
await p.evaluate(()=>{ timeLeft=1; }); await new Promise(r=>setTimeout(r,400)); const tm=await p.evaluate(()=>({enemies:candles.length,spawned:timeSpawned}));
// bombing the revealed exit spawns 2
await p.evaluate(()=>{ crates[exitTile.y][exitTile.x]=0; explode({x:exitTile.x-1,y:exitTile.y}); }); await new Promise(r=>setTimeout(r,300)); const ex=await p.evaluate(()=>({enemies:candles.length}));
// clear levels 1..5 by cheating, count transitions
const seen=[];
for(let i=0;i<5;i++){ await p.evaluate(()=>{ for(const c of candles) c.state='dead'; crates[exitTile.y][exitTile.x]=0; hero.x=exitTile.x; hero.y=exitTile.y; hero.px=hero.x*T; hero.py=hero.y*T; winT=0; deadT=0; });
  await new Promise(r=>setTimeout(r,8000)); seen.push(await p.evaluate(()=>({level,cleared,escaped,lives,WC,WR})));
  await p.keyboard.press('Space'); await new Promise(r=>setTimeout(r,6500)); }
await p.screenshot({path:'tests/out/escaped.png'});
const after=await p.evaluate(()=>({level,escaped,cleared,WC,lives}));
console.log('powerup',pu,'\ntimer',tm,'\nexit bombed',ex,'\nlevels',JSON.stringify(seen),'\nafter',after,'\nerrors',errs); await b.close();})();
