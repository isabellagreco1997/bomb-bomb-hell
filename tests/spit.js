const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.setViewport({width:1029,height:700}); await p.goto('http://127.0.0.1:8000/index.html'); await new Promise(r=>setTimeout(r,6000)); await p.click('#play'); await new Promise(r=>setTimeout(r,7000));
await p.evaluate(()=>{ level=2; applyLevel(2); genCrates(); spawnEnemies(); hero.x=1;hero.y=1;hero.px=T;hero.py=T; const c=candles[0]; c.x=5;c.y=1;c.px=5*T;c.py=T;c.speed=0; for(let x=2;x<5;x++) crates[1][x]=0; lives=3; hurtT=0; cam.x=0; cam.y=0; });
await new Promise(r=>setTimeout(r,200)); const s1=await p.evaluate(()=>({tele:candles[0].tele,flames:flames.length,SPIT})); await p.screenshot({path:'tests/out/spit_tell.png'});
await new Promise(r=>setTimeout(r,600)); await p.screenshot({path:'tests/out/spit.png'}); const s2=await p.evaluate(()=>({flames:flames.length,pos:flames[0]?[Math.round(flames[0].x/48*10)/10,Math.round(flames[0].y/48*10)/10]:null,lives}));
await new Promise(r=>setTimeout(r,2500)); const s3=await p.evaluate(()=>({flames:flames.length,lives,hurtT}));
console.log('tell',s1,'\nflame',s2,'\nafter',s3,'\nerrors',errs); await b.close();})();
