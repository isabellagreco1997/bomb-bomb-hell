const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('404'))errs.push(m.text())});
await p.setViewport({width:624,height:528}); await p.goto('http://127.0.0.1:8000/index.html?auto=1'); await new Promise(r=>setTimeout(r,4000));
const fps=await p.evaluate(()=>new Promise(res=>{let n=0;const t0=performance.now();function f(){n++; if(performance.now()-t0<2000) requestAnimationFrame(f); else res((n/2).toFixed(1));} requestAnimationFrame(f);}));
const st=await p.evaluate(()=>({bombs:bombs.length,fires:fires.length,hurt:hurtT,enemies:candles.map(c=>c.state+':'+c.hp).join(','),cam:[Math.round(cam.x),Math.round(cam.y)]}));
console.log('errors:',errs); console.log('fps:',fps,'state:',JSON.stringify(st)); await b.close();})();
