(() => {
  const canvas = document.querySelector('#pixel-current');
  const toggle = document.querySelector('#motion-toggle');
  if (!canvas || !toggle) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false, visible = true, frame = 0, last = 0, time = 0, width = 0;
  function draw() {
    ctx.clearRect(0, 0, width, 480);
    const scale = Math.min(width / 5.1, 82);
    const tilt = .6 + Math.sin(time * .18) * .15;
    const spin = time * .16;
    const dots = [];
    for (let i = 0; i < 94; i++) {
      const u = i / 94 * Math.PI * 2;
      for (let j = 0; j < 27; j++) {
        const v = j / 27 * Math.PI * 2;
        const r = 1.55 + .57 * Math.cos(v);
        const x = r * Math.cos(u), y = r * Math.sin(u), z = .57 * Math.sin(v);
        const xx = x * Math.cos(spin) + z * Math.sin(spin);
        const zz = -x * Math.sin(spin) + z * Math.cos(spin);
        const yy = y * Math.cos(tilt) - zz * Math.sin(tilt);
        const depth = y * Math.sin(tilt) + zz * Math.cos(tilt);
        dots.push({x:width/2+xx*scale,y:230+yy*scale,z:depth});
      }
    }
    dots.sort((a,b)=>a.z-b.z);
    for (const dot of dots) {
      const front = (dot.z + 2.3) / 4.6;
      const size = 1.2 + front * 2.2;
      ctx.fillStyle = `rgba(194,65,28,${.12+front*.78})`;
      ctx.fillRect(dot.x,dot.y,size,size);
    }
  }

  function tick(now) {
    if (last) time += Math.min((now-last)/1000,.05);
    last = now; draw(); frame = requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame); last = 0;
    toggle.hidden = reduced.matches;
    toggle.textContent = paused ? 'Resume motion' : 'Pause motion';
    toggle.setAttribute('aria-pressed', String(paused));
    document.documentElement.classList.toggle('motion-paused', paused || reduced.matches);
    if (!paused && !reduced.matches && visible && !document.hidden) frame = requestAnimationFrame(tick);
    else draw();
  }
  function resize() {
    width = canvas.getBoundingClientRect().width;
    const ratio = Math.min(devicePixelRatio || 1,2);
    canvas.width = width * ratio; canvas.height = 480 * ratio;
    ctx.setTransform(ratio,0,0,ratio,0,0); draw(); sync();
  }
  toggle.addEventListener('click',()=>{paused=!paused;sync();});
  reduced.addEventListener('change',sync);
  document.addEventListener('visibilitychange',sync);
  addEventListener('resize',resize,{passive:true});
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();}).observe(canvas);
    const observer = new IntersectionObserver(entries=>{
      entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-seen');observer.unobserve(entry.target);}});
    });
    document.querySelectorAll('.flow-list li').forEach(step=>observer.observe(step));
  }
  resize();
})();
