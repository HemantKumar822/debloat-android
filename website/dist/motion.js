(() => {
  const canvas = document.querySelector('#page-pixels');
  const toggle = document.querySelector('#motion-toggle');
  if (!canvas || !toggle) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) {toggle.hidden=true;return;}
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused=false, frame=0, last=0, time=0, width=0, height=0, progress=0, scrollOffset=0;
  function draw() {
    ctx.clearRect(0,0,width,height);
    const edge = width < 700 ? 16 : Math.min(85,width*.055);
    for(let i=0;i<48;i++) {
      const side=i%2;
      const x=side ? width-((i*37)%edge)-5 : ((i*37)%edge)+3;
      const y=((i*97+time*(4+i%4)+scrollOffset*.12)%(height+70))-35;
      const opacity=.08+.12*(1+Math.sin(time*.35+i))/2;
      ctx.fillStyle=i%5===0 ? `rgba(180,100,67,${opacity})` : `rgba(210,84,40,${opacity})`;
      const size=i%7===0?6:3;
      ctx.fillRect(x,y,size,size);
    }
    // A pixel reading-progress line and small margin mosaics grow with the page.
    const cell=12, count=Math.ceil(width/cell);
    for(let i=0;i<count;i++) {
      ctx.fillStyle=i/count<progress?'rgba(190,59,22,.65)':'rgba(190,59,22,.045)';
      ctx.fillRect(i*cell,0,8,3);
    }
    if(width>=700) for(let side=0;side<2;side++) {
      for(let row=0;row<10;row++) for(let col=0;col<3;col++) {
        const index=row*3+col;
        const active=index/30<progress;
        const x=side?width-19-col*9:12+col*9;
        const y=height-42-(9-row)*9;
        ctx.fillStyle=active?`rgba(190,59,22,${.15+.2*(col+1)/3})`:'rgba(160,137,115,.055)';
        ctx.fillRect(x,y,4,4);
      }
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
  resize();
})();
