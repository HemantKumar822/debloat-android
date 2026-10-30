(() => {
  const canvas = document.querySelector('#pixel-current');
  const toggle = document.querySelector('#motion-toggle');
  if (!canvas || !toggle) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false, visible = true, frame = 0, last = 0, time = 0, width = 0;
  function draw() {
    ctx.clearRect(0, 0, width, 150);
    for (let row = 0; row < 15; row++) {
      for (let col = 0; col < width / 12; col++) {
        const x = col * 12, u = x / Math.max(width, 1);
        const y = 75 + Math.sin(u * 8 + time * .35 + row * .15) * 25 + (row - 7) * 5;
        const alpha = Math.sin(u * Math.PI) * (.23 + .12 * Math.sin(u * 9 - time * .4 + row * .4));
        ctx.fillStyle = `rgba(195,58,22,${Math.max(0,alpha)})`;
        ctx.fillRect(x,y,row % 4 === 0 ? 3 : 2, row % 4 === 0 ? 3 : 2);
      }
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
    canvas.width = width * ratio; canvas.height = 150 * ratio;
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
