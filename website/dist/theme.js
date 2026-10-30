(() => {
 const button=document.getElementById('theme-toggle');if(!button)return;
 const media=matchMedia('(prefers-color-scheme: dark)'),reduce=matchMedia('(prefers-reduced-motion: reduce)');
 let saved;try{saved=localStorage.getItem('debloat-theme');}catch{}
 function apply(dark){document.documentElement.dataset.theme=dark?'dark':'light';button.setAttribute('aria-label',dark?'Switch to light mode':'Switch to dark mode');button.setAttribute('aria-pressed',String(dark));}
 apply(saved?saved==='dark':media.matches);
 media.addEventListener('change',()=>{if(!saved)apply(media.matches);});
 button.addEventListener('click',async event=>{
  const dark=document.documentElement.dataset.theme!=='dark';
  const change=()=>{apply(dark);saved=dark?'dark':'light';try{localStorage.setItem('debloat-theme',saved);}catch{}};
  if(!document.startViewTransition||reduce.matches){change();return;}
  button.disabled=true;
  const rect=button.getBoundingClientRect(),x=event.clientX||rect.x+rect.width/2,y=event.clientY||rect.y+rect.height/2;
  try{const transition=document.startViewTransition(change);await transition.ready;
   await document.documentElement.animate({clipPath:[`circle(0px at ${x}px ${y}px)`,`circle(${Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y))}px at ${x}px ${y}px)`]},{duration:650,easing:'cubic-bezier(.2,.8,.2,1)',pseudoElement:'::view-transition-new(root)'}).finished;
  }catch{apply(dark);}finally{button.disabled=false;}
 });
})();
