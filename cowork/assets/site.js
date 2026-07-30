
document.querySelectorAll('.copy-btn').forEach(btn=>{
 btn.addEventListener('click', async ()=>{
   const code=btn.parentElement.querySelector('pre code')||btn.parentElement.querySelector('pre');
   try{await navigator.clipboard.writeText(code.innerText);btn.textContent='הועתק';setTimeout(()=>btn.textContent='העתקת פרומפט',1500)}
   catch(e){btn.textContent='סמנו והעתיקו ידנית'}
 });
});
document.querySelectorAll('.toggle-shot').forEach(btn=>{
 btn.addEventListener('click',()=>{
   const card=btn.closest('.shot-card');
   const img=card.querySelector('img');
   const link=card.querySelector('a');
   const showingAnnotated=img.src.includes('-annotated.jpg');
   const next=showingAnnotated?btn.dataset.clean:btn.dataset.annotated;
   img.src=next;link.href=next;
   btn.textContent=showingAnnotated?'הצגת סימונים':'הצגת צילום נקי';
 });
});
document.querySelectorAll('table').forEach(t=>{const w=document.createElement('div');w.className='table-wrapper';t.parentNode.insertBefore(w,t);w.appendChild(t)});
