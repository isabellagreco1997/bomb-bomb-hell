const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new'});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.setViewport({width:624,height:528}); await p.goto('http://127.0.0.1:8000/index.html'); await new Promise(r=>setTimeout(r,1500));
await p.keyboard.press('Space'); await new Promise(r=>setTimeout(r,200));
const pos=async()=>await p.evaluate(()=>[hero.x,hero.y,started,JSON.stringify(keys)]);
console.log('start',await pos());
for(const k of ['ArrowDown','ArrowRight','ArrowUp','ArrowLeft']){ await p.keyboard.down(k); await new Promise(r=>setTimeout(r,900)); await p.keyboard.up(k); await new Promise(r=>setTimeout(r,300)); console.log(k,await pos()); }
console.log('errors',errs); await b.close();})();
