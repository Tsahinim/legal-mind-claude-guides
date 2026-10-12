(()=>{"use strict";const sections=[...document.querySelectorAll(".guide-section[id]")],links=[...document.querySelectorAll(".desktop-toc a[href^='#']")];if(!sections.length||!links.length)return;const set=id=>links.forEach(a=>a.getAttribute("href")==="#"+id?a.setAttribute("aria-current","location"):a.removeAttribute("aria-current"));set(sections[0].id);if("IntersectionObserver"in window){const o=new IntersectionObserver(es=>{const v=es.filter(e=>e.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];if(v)set(v.target.id)},{rootMargin:"-15% 0px -65% 0px",threshold:[0,.15,.5]});sections.forEach(s=>o.observe(s))}})();
(()=>{"use strict";
// היעד נמצא בתוך תיבת ההעתקה עצמה, ולא לפי מזהה גלובלי. getElementById
// מחזיר את הראשון במסמך, וכשלפרק ולתיבה היה אותו מזהה הוא החזיר את הפרק
// והכפתור העתיק פרק שלם במקום פרומפט.
document.querySelectorAll(".copy-button[data-copy-target]").forEach(btn=>{
 const orig=btn.textContent;
 btn.addEventListener("click",async()=>{
  const box=btn.closest(".copy-block");
  const el=(box&&box.querySelector(".copy-body"))
        ||document.getElementById(btn.getAttribute("data-copy-target"));
  if(!el)return;
  const status=box?box.querySelector(".copy-status"):null;
  const done=msg=>{btn.textContent="הועתק";if(status)status.textContent=msg;
   setTimeout(()=>{btn.textContent=orig;if(status)status.textContent=""},2500);};
  const text=el.innerText.trim();
  try{await navigator.clipboard.writeText(text);done("הטקסט הועתק.");}
  catch(e){
   // גיבוי לדפדפנים שחוסמים את הלוח
   try{const t=document.createElement("textarea");t.value=text;
    t.setAttribute("readonly","");t.style.position="fixed";t.style.top="-1000px";
    document.body.appendChild(t);
    let copied=false;
    try{t.select();t.setSelectionRange(0,t.value.length);copied=document.execCommand("copy");}
    finally{t.remove();btn.focus({preventScroll:true});}
    if(!copied)throw new Error("Copy blocked");
    done("הטקסט הועתק.");}
   catch(e2){if(status)status.textContent=
    "ההעתקה נחסמה בדפדפן. סמנו את הטקסט והעתיקו ידנית.";}
  }
 });
});
})();

(()=>{"use strict";
const HINT="לחיצה על התמונה מגדילה אותה, עם אפשרות לגלול בתוכה לכל הכיוונים.";
let box=null,scroll=null,pic=null,opener=null,previousOverflow="";
let background=[];
const build=()=>{
 box=document.createElement("div");
 box.className="lightbox";
 box.setAttribute("role","dialog");
 box.setAttribute("aria-modal","true");
 box.setAttribute("aria-label","תצוגה מוגדלת של הצילום");
 box.innerHTML='<button class="lightbox-close" type="button">סגירה</button>'+
  '<div class="lightbox-scroll" tabindex="0" aria-label="צילום מוגדל, ניתן לגלול במגע או במקשי החצים"><div class="lightbox-frame"><img alt=""></div></div>'+
  '<p class="lightbox-hint">גררו או גללו כדי לנוע בתמונה. סגירה במקש Esc.</p>';
 document.body.appendChild(box);
 scroll=box.querySelector(".lightbox-scroll");
 pic=box.querySelector("img");
 pic.draggable=false;
 box.querySelector(".lightbox-close").addEventListener("click",close);
 box.addEventListener("click",e=>{if(e.target===box)close();});
 let down=false,sx=0,sy=0,l=0,t=0;
 scroll.addEventListener("pointerdown",e=>{if(e.pointerType!=="mouse"||e.button!==0)return;e.preventDefault();down=true;sx=e.clientX;sy=e.clientY;l=scroll.scrollLeft;t=scroll.scrollTop;scroll.classList.add("is-dragging");scroll.setPointerCapture(e.pointerId);});
 scroll.addEventListener("pointermove",e=>{if(!down)return;scroll.scrollLeft=l-(e.clientX-sx);scroll.scrollTop=t-(e.clientY-sy);});
 const up=e=>{down=false;scroll.classList.remove("is-dragging");};
 scroll.addEventListener("pointerup",up);
 scroll.addEventListener("pointercancel",up);
};
const close=()=>{
 if(!box||!box.classList.contains("is-open"))return;
 box.classList.remove("is-open");pic.onload=null;
 document.body.style.overflow=previousOverflow;
 background.forEach(([el,wasInert])=>{el.inert=wasInert;});background=[];
 if(opener&&opener.isConnected)opener.focus({preventScroll:true});
};
// הגדלה אמיתית: בלי זה התמונה נפתחת בגודלה הטבעי, וכשהיא גדולה מהמסך
// שום דבר לא גדל והחלון רק מוסיף רקע כהה מסביב.
const fit=shown=>{
 const nat=pic.naturalWidth;if(!nat)return;
 const vw=Math.max(document.documentElement.clientWidth,320);
 const want=Math.max(nat,(shown||nat)*1.8,vw*1.2);
 pic.style.width=Math.round(Math.min(nat*2.2,want))+"px";
 pic.parentElement.style.width=pic.style.width;
 // פתיחה במרכז: חלק מהצילומים הם גיליון בעברית שמתחיל מימין, וחלק
 // מסכי Office באנגלית שמתחילים משמאל, ואין דרך לדעת מראש מי מי
 scroll.scrollTop=0;
 scroll.scrollLeft=(scroll.scrollWidth-scroll.clientWidth)/2;
};
const open=(src,alt,shown,trigger)=>{
 if(!box)build();
 opener=trigger||document.activeElement;
 previousOverflow=document.body.style.overflow;
 background=[...document.body.children].filter(el=>el!==box).map(el=>[el,el.inert]);
 background.forEach(([el])=>{el.inert=true;});
 pic.onload=()=>fit(shown);
 pic.style.width="";
 const shownImage=trigger?.matches('img')?trigger:trigger?.closest('.shot')?.querySelector('img');
 box.querySelectorAll('.shot-target').forEach(el=>el.remove());
 // Percentage annotations remain correct only when opening the same image.
 if(shownImage&&new URL(src,document.baseURI).href===(shownImage.currentSrc||shownImage.src)){
  shownImage.closest('.shot-frame')?.querySelectorAll('.shot-target').forEach(el=>pic.parentElement.appendChild(el.cloneNode(true)));
 }
 pic.src=src;pic.alt=alt||"";
 box.classList.add("is-open");
 document.body.style.overflow="hidden";
 if(pic.complete)fit(shown);
 box.querySelector(".lightbox-close").focus();
};
document.querySelectorAll('.shot a[href$=".png"]').forEach(a=>{
 a.addEventListener("click",e=>{
  e.preventDefault();
  const im=a.querySelector("img")||a.closest(".shot").querySelector("img");
  open(a.getAttribute("href"),im?im.alt:"",im?im.clientWidth:0,a);
 });
});
const arm=img=>{
 if(img.closest("a")||img.classList.contains("is-zoomable"))return;
 img.classList.add("is-zoomable");
 img.tabIndex=0;img.setAttribute("role","button");
 img.setAttribute("aria-label","הגדלת צילום: "+img.alt);
 img.addEventListener("click",()=>open(img.currentSrc||img.src,img.alt,img.clientWidth,img));
 img.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();img.click();}});
 // כל צילום ניתן להגדלה, אבל ההערה מתחתיו מופיעה רק כשהחיתוך הקטין אותו
 if(img.naturalWidth<=img.clientWidth+4)return;
 const fig=img.closest(".shot");
 if(fig&&!fig.querySelector(".shot-zoom")){
  const p=document.createElement("p");
  p.className="shot-zoom";p.textContent=HINT;fig.appendChild(p);
 }
};
const scan=()=>document.querySelectorAll(".shot img").forEach(img=>{
 img.complete?arm(img):img.addEventListener("load",()=>arm(img),{once:true});
});
window.addEventListener("load",scan);

document.addEventListener("keydown",e=>{
 if(!box||!box.classList.contains("is-open"))return;
 if(e.key==="Escape"){e.preventDefault();close();}
 if(e.key==="Tab"){
  e.preventDefault();
  (document.activeElement===box.querySelector(".lightbox-close")?scroll:box.querySelector(".lightbox-close")).focus();
 }
});
})();

// הדפסת רשימת הבדיקה בלבד: המדריך מבטיח שאפשר לתלות אותה על הקיר,
// ובלי זה הדפסה מוציאה את כל המדריך
(()=>{"use strict";
const b=document.querySelector(".print-checklist");if(!b)return;
b.addEventListener("click",()=>{
 document.body.classList.add("only-checklist");
 const off=()=>document.body.classList.remove("only-checklist");
 window.addEventListener("afterprint",off,{once:true});
 setTimeout(off,4000);
 window.print();
});
})();

// Collapse the mobile contents before the browser resolves the anchor position.
document.querySelectorAll('.mobile-toc a[href^="#"]').forEach(a=>{
 a.addEventListener('click',()=>{const details=a.closest('details');if(details)details.open=false;});
});
