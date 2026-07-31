
document.querySelectorAll('.copy-btn').forEach(btn=>{
 const original=btn.textContent;
 btn.addEventListener('click', async ()=>{
   const code=btn.parentElement.querySelector('pre code')||btn.parentElement.querySelector('pre');
   try{await navigator.clipboard.writeText(code.innerText);btn.textContent='הועתק';setTimeout(()=>btn.textContent=original,1500)}
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

/* scrollspy: highlight the section currently in view in the sidebar TOC */
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.sidebar a[href^="#"]'));
  var map = links.map(function (a) {
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    return { a: a, t: document.getElementById(id) };
  }).filter(function (x) { return x.t; });
  if (!map.length) return;
  function onScroll() {
    var y = window.scrollY + 140, cur = map[0];
    map.forEach(function (x) { if (x.t.offsetTop <= y) cur = x; });
    links.forEach(function (a) { a.classList.toggle('current', a === cur.a); });
    var sb = document.querySelector('.sidebar');
    if (sb && cur) {
      var t = cur.a.offsetTop - sb.offsetTop;
      if (t < sb.scrollTop + 40 || t > sb.scrollTop + sb.clientHeight - 60) {
        sb.scrollTo({ top: Math.max(0, t - sb.clientHeight / 2), behavior: "smooth" });
      }
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
