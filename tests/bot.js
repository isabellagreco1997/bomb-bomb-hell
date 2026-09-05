const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.setViewport({width:1029,height:700}); await p.goto('http://127.0.0.1:8000/index.html?bot=1'); await new Promise(r=>setTimeout(r,12000));
let last='', t0=Date.now(), maxS=parseInt(process.argv[2]||'260');
while((Date.now()-t0)/1000<maxS){ await new Promise(r=>setTimeout(r,2000));
  const s=await p.evaluate(()=>({lvl:level,alive:candles.filter(c=>c.state==='alive').length,crates:crates.flat().filter(v=>v>0).length,lives,time:Math.ceil(timeLeft/60),score,pos:[hero.x,hero.y],bombs:bombs.length,exitOpen:exitTile&&crates[exitTile.y][exitTile.x]===0,power:powerTile&&powerTile.taken,win:winT>0,clear:cleared,over:gameOver,stuck:botState.stuck,ready}));
  const key=JSON.stringify([s.lvl,s.alive,s.crates,s.lives,s.exitOpen,s.power,s.win,s.clear,s.over]);
  if(key!==last){ console.log(((Date.now()-t0)/1000).toFixed(0)+'s',JSON.stringify(s)); last=key; }
  if(s.clear||s.over){ await p.screenshot({path:'tests/out/bot_end.png'}); break; } }
console.log('errors',errs); await b.close();})();
