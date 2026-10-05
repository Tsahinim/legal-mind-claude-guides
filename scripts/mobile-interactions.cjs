const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const output=path.resolve('../mobile-qa');fs.mkdirSync(output,{recursive:true});
const root='http://localhost:4173';
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,permissions:['clipboard-read','clipboard-write'],reducedMotion:'reduce'});
 const page=await context.newPage();
 const report=[];
 for(const route of ['/excel/guide-1/','/excel/guide-2/','/excel/guide-3/','/excel/bonus/']){
  await page.goto(root+route);
  await page.evaluate(async()=>{for(const i of document.images)i.loading='eager';await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));});
  const copies=page.locator('.copy-button');
  for(let i=0;i<await copies.count();i++){
   const button=copies.nth(i);
   const expected=await button.evaluate(b=>(b.closest('.copy-block')?.querySelector('.copy-body')||document.getElementById(b.dataset.copyTarget)).innerText.trim());
   await button.click();
   await page.waitForFunction(()=>document.querySelector('.copy-button:focus')?.textContent==='הועתק');
   assert.equal((await page.evaluate(()=>navigator.clipboard.readText())).replaceAll('\r\n','\n'),expected);
  }
  const details=page.locator('.mobile-toc details');
  await details.locator('summary').click();
  const lastLink=details.locator('a').last();const href=await lastLink.getAttribute('href');
  await lastLink.click();await page.waitForTimeout(120);
  assert.equal(await details.getAttribute('open'),null);
  assert.equal(new URL(page.url()).hash,href);
  const targetTop=await page.locator(href).evaluate(e=>e.getBoundingClientRect().top);
  assert(targetTop>=-1&&targetTop<100,`Anchor target top ${targetTop}`);
  const shot=page.locator('.shot img.is-zoomable').first();
  if(await shot.count()){
   await shot.scrollIntoViewIfNeeded();await shot.tap();
   await page.waitForFunction(()=>{const i=document.querySelector('.lightbox img');return i?.naturalWidth&&parseFloat(i.style.width)>=i.naturalWidth;});
   const geometry=await page.evaluate(()=>{const s=document.querySelector('.lightbox-scroll'),b=document.querySelector('.lightbox-close');return {left:s.scrollLeft,max:s.scrollWidth-s.clientWidth,scrollTop:s.getBoundingClientRect().top,buttonBottom:b.getBoundingClientRect().bottom};});
   assert(Math.abs(geometry.left-geometry.max/2)<2,'Zoom center');
   assert(geometry.scrollTop>=geometry.buttonBottom,'Close button overlaps image');
   assert.equal(await page.locator('.lightbox .shot-target').count(),await shot.evaluate(e=>e.closest('.shot-frame').querySelectorAll('.shot-target').length),'Screenshot annotations preserved');
   const touch=await context.newCDPSession(page);
   await touch.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:240,y:300}]});
   for(const x of [220,200,180,160,140]){await touch.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:300}]});await page.waitForTimeout(25);}
   await touch.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   await page.waitForTimeout(180);
   assert((await page.locator('.lightbox-scroll').evaluate(e=>e.scrollLeft))>geometry.left+20,'Touch can pan enlarged image');
   await touch.detach();
   await page.keyboard.press('Tab');assert(await page.locator('.lightbox-scroll').evaluate(e=>e===document.activeElement));
   await page.keyboard.press('Tab');assert(await page.locator('.lightbox-close').evaluate(e=>e===document.activeElement));
   await page.screenshot({path:path.join(output,route.split('/')[2]+'-zoom-390.png')});
   await page.locator('.lightbox-close').tap();
   assert(await shot.evaluate(e=>e===document.activeElement),'Focus restored');
   assert.equal(await page.locator('body').evaluate(e=>e.style.overflow),'');
   assert.equal(await page.locator('[inert]').count(),0);
   await shot.press('Enter');await page.keyboard.press('Escape');
   assert.equal(await page.locator('.lightbox.is-open').count(),0);
  }
  report.push({route,copyButtons:await copies.count(),toc:true,zoom:!!await shot.count()});
  console.log(JSON.stringify(report.at(-1)));
 }
 // A blocked browser must never report a successful copy.
 await context.clearPermissions();
 await page.goto(root+'/excel/bonus/');
 await page.evaluate(()=>{Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(Error('Blocked'))},configurable:true});document.execCommand=()=>false;});
 await page.locator('.copy-button').first().click();
 await page.waitForFunction(()=>document.querySelector('.copy-status').textContent.includes('נחסמה'));
 assert.notEqual(await page.locator('.copy-button').first().innerText(),'הועתק');
 // Capture narrow text tables and the download button, not only page headers.
 await page.setViewportSize({width:320,height:844});
 await page.locator('a[download]').first().scrollIntoViewIfNeeded();
 await page.screenshot({path:path.join(output,'bonus-download-320.png')});
 for(const [route,selector,name] of [['/excel/guide-2/','table','schedule-320'],['/excel/guide-3/','#dont-ask','limits-320']]){
  await page.goto(root+route);await page.locator(selector).first().scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(output,name+'.png')});
 }
 fs.writeFileSync(path.join(output,'interactions.json'),JSON.stringify({report,blockedClipboard:true},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
