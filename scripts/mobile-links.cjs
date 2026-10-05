const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {execFileSync,spawnSync}=require('node:child_process');
const root=process.cwd(),output=path.resolve('../mobile-qa');
const files=['excel/index.html',...[1,2,3].map(n=>`excel/guide-${n}/index.html`),'excel/bonus/index.html'];
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const page=await browser.newPage();
 let links=0,images=0,downloads=0,anchors=0;const checked=new Set();
 for(const file of files){
  const original=execFileSync('git',['show','HEAD:'+file],{encoding:'utf8',maxBuffer:10*1024*1024});
  const texts=await page.evaluate(sources=>sources.map(html=>{
   const doc=new DOMParser().parseFromString(html,'text/html');
   // The requested community/footer and repaired image descriptions are checked
   // separately. All existing teaching text and screenshot legends must remain.
   doc.querySelectorAll('style,script,.lm-community-area,footer,.shot-frame,img').forEach(e=>e.remove());
   return doc.body.textContent.replace(/\s+/g,' ').trim();
  }),[original,fs.readFileSync(file,'utf8')]);
  assert.equal(texts[0],texts[1],'Professional content changed: '+file);
  await page.goto('http://localhost:4173/'+file);
  const data=await page.evaluate(()=>({ids:[...document.querySelectorAll('[id]')].map(e=>e.id),links:[...document.querySelectorAll('a[href],link[href],script[src],img[src]')].map(e=>({url:e.href||e.src,tag:e.tagName,download:e.hasAttribute('download')}))}));
  assert.equal(data.ids.length,new Set(data.ids).size,'Duplicate IDs: '+file);
  for(const item of data.links){
   if(!item.url.startsWith('http://localhost:4173/'))continue;
   const u=new URL(item.url);let local=path.join(root,decodeURIComponent(u.pathname));
   if(u.pathname.endsWith('/'))local=path.join(local,'index.html');
   assert(fs.existsSync(local),'Missing resource: '+local);
   if(u.hash){const html=fs.readFileSync(local,'utf8'),id=decodeURIComponent(u.hash.slice(1));assert(html.includes('id="'+id+'"')||html.includes("id='"+id+"'"),'Missing anchor '+item.url);anchors++;}
   if(item.tag==='A')links++;if(item.tag==='IMG')images++;if(item.download)downloads++;
   checked.add(local);
  }
 }
 const qa=spawnSync(process.execPath,['scripts/qa.mjs'],{encoding:'utf8',maxBuffer:20*1024*1024});
 assert.equal(qa.status,0,'Repository QA failed: '+qa.stderr.slice(0,2000));
 const lines=(qa.stdout+'\n'+qa.stderr).split(/\r?\n/).filter(Boolean).map(s=>s.length>600?s.slice(0,600)+' [truncated]':s);
 fs.writeFileSync(path.join(output,'repository-qa.txt'),lines.join('\n'));
 const report={pages:files.length,links,images,downloads,anchors,resources:checked.size,teachingContentUnchanged:true,repositoryQaExitCode:qa.status,repositoryQaMessages:lines.length};
 fs.writeFileSync(path.join(output,'links.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
