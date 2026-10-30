(() => {
  const canvas = document.querySelector('#page-pixels');
  const toggle = document.querySelector('#motion-toggle');
  if (!canvas || !toggle) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) {toggle.hidden=true;return;}
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused=false, frame=0, last=0, time=0, width=0, height=0, progress=0, scrollOffset=0, mouse={x:-1000,y:-1000};
  function draw() {
    ctx.clearRect(0,0,width,height);
    const edge = width < 700 ? 16 : Math.min(85,width*.055);
    for(let i=0;i<48;i++) {
      const side=i%2;
      let x=side ? width-((i*37)%edge)-5 : ((i*37)%edge)+3;
      let y=((i*97+time*(4+i%4)+scrollOffset*.12)%(height+70))-35;
      if(!paused&&!reduced.matches){const dx=x-mouse.x,dy=y-mouse.y,d=Math.hypot(dx,dy);if(d<120&&d>0){x+=dx/d*(120-d)*.25;y+=dy/d*(120-d)*.25;}}
      const opacity=.08+.12*(1+Math.sin(time*.35+i))/2;
      ctx.fillStyle=i%5===0 ? `rgba(180,100,67,${opacity})` : `rgba(210,84,40,${opacity})`;
      const size=i%7===0?6:3;
      ctx.fillRect(x,y,size,size);
    }
  }

  function measureScroll() {
    scrollOffset=scrollY;
    const range=document.documentElement.scrollHeight-innerHeight;
    progress=range>0?Math.max(0,Math.min(1,scrollOffset/range)):0;
    if(paused||reduced.matches)draw();
  }

  function tick(now) {
    if(last) time+=Math.min((now-last)/1000,.05);
    last=now;draw();frame=requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame);last=0;
    toggle.hidden=reduced.matches;
    toggle.textContent=paused?'Resume motion':'Pause motion';
    toggle.setAttribute('aria-pressed',String(paused));
    if(!paused&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick);
    else draw();
  }
  function resize(){width=innerWidth;height=innerHeight;const dpr=Math.min(devicePixelRatio||1,2);canvas.width=width*dpr;canvas.height=height*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);measureScroll();draw();sync();}
  toggle.addEventListener('click',()=>{paused=!paused;sync();});
  reduced.addEventListener('change',sync);
  document.addEventListener('visibilitychange',sync);
  addEventListener('resize',resize,{passive:true});
  addEventListener('scroll',measureScroll,{passive:true});
  addEventListener('pointermove',event=>{if(event.pointerType==='mouse')mouse={x:event.clientX,y:event.clientY};},{passive:true});
  resize();
})();
