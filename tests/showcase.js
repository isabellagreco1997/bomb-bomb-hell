const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.setViewport({width:736,height:600}); await p.goto('http://127.0.0.1:8000/index.html?showcase=1');
let last=''; const t0=Date.now();
for(let i=0;i<150;i++){ await new Promise(r=>setTimeout(r,500));
  const s=await p.evaluate(()=>({cap:caption,lives,ready,deadT,winT,cleared,gameOver,hero:[hero.x,hero.y],bombs:bombs.length,en:candles.map(c=>c.state+':'+c.hp).join(',')}));
  const key=s.cap+'|'+s.lives+'|'+s.ready+'|'+(s.deadT>0)+'|'+(s.winT>0)+'|'+s.cleared+'|'+s.gameOver;
  if(key!==last){ console.log(((Date.now()-t0)/1000).toFixed(1)+'s',JSON.stringify(s)); last=key; }
  if(s.cap==='end of showcase') break; }
console.log('errors',errs); await b.close();})();
