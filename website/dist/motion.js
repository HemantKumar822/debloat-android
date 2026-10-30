(() => {
  const canvas = document.querySelector('#page-pixels');
  const toggle = document.querySelector('#motion-toggle');
  if (!canvas || !toggle) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) {toggle.hidden=true;return;}
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused=false, frame=0, last=0, time=0, width=0, height=0, scrollOffset=0, mouse={x:-1000,y:-1000};
  function draw() {
    ctx.clearRect(0,0,width,height);
    const dark=document.documentElement.dataset.theme==='dark';
    const pitch=width<700?44:38;
    // A quiet lattice across the entire viewport, with a travelling diagonal current.
    // The pointer reveals a little of the field; it never moves the page content.
    for(let col=0;col<Math.ceil(width/pitch);col++) {
      for(let row=-1;row<Math.ceil(height/pitch)+1;row++) {
        const x=col*pitch+pitch/2;
        const y=row*pitch+(scrollOffset*.08)%pitch;
        const distance=Math.hypot(x-mouse.x,y-mouse.y);
        const hover=!paused&&!reduced.matches?Math.max(0,1-distance/180):0;
        const wave=Math.pow(Math.max(0,Math.sin(col*.19+row*.25-time*.65)),12);
        const margin=Math.min(x,width-x)<width*.12;
        const opacity=(dark?.025:.018)+wave*(margin?.12:.025)+hover*.16;
        const size=hover>.55||wave>.8&&margin?3:1.4;
        ctx.fillStyle=`rgba(${dark?'240,154,119':'185,80,42'},${opacity})`;
        ctx.fillRect(Math.round(x),Math.round(y),size,size);
      }
    }
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
  document.addEventListener('pointerleave',()=>{mouse={x:-1000,y:-1000};});
  resize();
})();
