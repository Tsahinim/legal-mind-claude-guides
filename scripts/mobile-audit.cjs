const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const output = process.env.QA_OUTPUT || path.resolve('../mobile-qa');
fs.mkdirSync(output, { recursive: true });
const pages = ['/', '/excel/', '/excel/guide-1/', '/excel/guide-2/', '/excel/guide-3/', '/excel/bonus/'];
(async () => {
  const browser = await chromium.launch({channel:'chrome', headless:true});
  const results = [];
  for (const width of [320, 390, 768, 820, 1024, 1440]) {
    const context = await browser.newContext({viewport:{width,height:844}, hasTouch:width<=820, isMobile:width<=820});
    for (const route of pages) {
      const page = await context.newPage();
      const errors=[]; page.on('pageerror',e=>errors.push(e.message));
      await page.goto('http://localhost:4173'+route, {waitUntil:'load'});
      await page.evaluate(async()=>{for(const img of document.images)img.loading='eager';await Promise.all([...document.images].map(img=>img.decode().catch(()=>{})));});
      const data=await page.evaluate(()=>{
        const visible=e=>e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
        const overflow=[...document.querySelectorAll('body *')].filter(visible).filter(e=>{
          if(e.closest('.tbl-wrap,.lightbox,.skip,.skip-link'))return false;
          const r=e.getBoundingClientRect();return r.left < -1 || r.right > innerWidth+1;
        }).map(e=>({tag:e.tagName,cls:e.className,text:e.textContent.trim().slice(0,70),left:Math.round(e.getBoundingClientRect().left),width:Math.round(e.getBoundingClientRect().width)}));
        return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,overflow:overflow.slice(0,15),overflowCount:overflow.length, brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),tables:[...document.querySelectorAll('table')].map(t=>({cols:t.rows[0]?.cells.length,width:Math.round(t.getBoundingClientRect().width),container:Math.round(t.parentElement.getBoundingClientRect().width)}))};
      });
      results.push({route,width,...data,errors});
      console.log(JSON.stringify({route,width,overflow:data.overflowCount,brokenImages:data.brokenImages.length,errors}));
      if(width===390) await page.screenshot({path:path.join(output,route.replaceAll('/','_')+'-390.png'),fullPage:route==='/'||route==='/excel/'});
      await page.close();
    }
    await context.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(output,'layout.json'),JSON.stringify(results,null,2));
  if(results.some(r=>r.overflowCount||r.brokenImages.length||r.errors.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
