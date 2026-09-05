// capture a gif of the page: node gifcap.js <url> <outdir> <seconds> <fps> [clickPlay]
const puppeteer=require('puppeteer-core');
const [url,out,secs,fps,click]=process.argv.slice(2);
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); await p.setViewport({width:1029,height:700}); await p.goto(url); await new Promise(r=>setTimeout(r,click?6000:800));
if(click){ try{ await p.click('#play'); }catch(e){} await new Promise(r=>setTimeout(r,parseInt(click))); }
const n=Math.round(secs*fps); const el=await p.$(click?'#c':'#titlebox');
for(let i=0;i<n;i++){ const t0=Date.now(); await el.screenshot({path:`${out}/f_${String(i).padStart(3,'0')}.png`}); const dt=Date.now()-t0; await new Promise(r=>setTimeout(r,Math.max(0,1000/fps-dt))); }
await b.close();})();
