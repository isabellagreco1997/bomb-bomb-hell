const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:'new',args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('404'))errs.push(m.text())});
await p.setViewport({width:1029,height:700}); await p.goto('http://127.0.0.1:8000/index.html'); await new Promise(r=>setTimeout(r,6000));
await p.screenshot({path:'tests/out/title_new.png'});
const t0=await p.evaluate(()=>({playDisabled:document.getElementById('play').disabled, cls:document.getElementById('title').className}));
await p.click('#play'); await new Promise(r=>setTimeout(r,7000));
const s1=await p.evaluate(()=>({titleShown:getComputedStyle(document.getElementById('title')).display!=='none',started,ready,level,WC,WR,enemies:candles.length,exit:exitTile,power:powerTile,time:Math.ceil(timeLeft/60)}));
await p.screenshot({path:'tests/out/level1.png'});
// cheat through level 1: kill all, reveal the exit, stand on it
await p.evaluate(()=>{ for(const c of candles) c.state='dead'; crates[exitTile.y][exitTile.x]=0; hero.x=exitTile.x; hero.y=exitTile.y; hero.px=hero.x*T; hero.py=hero.y*T; });
await new Promise(r=>setTimeout(r,800)); const s2=await p.evaluate(()=>({winT,score,lives}));
await new Promise(r=>setTimeout(r,7000)); const s3=await p.evaluate(()=>({cleared,level})); await p.screenshot({path:'tests/out/level1_clear.png'});
await p.keyboard.press('Space'); await new Promise(r=>setTimeout(r,6000));
const s4=await p.evaluate(()=>({level,WC,WR,enemies:candles.length,lives,ready,time:Math.ceil(timeLeft/60),bombCap,RANGE}));
await p.screenshot({path:'tests/out/level2.png'});
console.log('title',t0,'\nlevel1',s1,'\nwin',s2,'\nclear',s3,'\nlevel2',s4,'\nerrors',errs); await b.close();})();
