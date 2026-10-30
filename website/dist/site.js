(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const animateIn = node => {
    if (!reduced.matches && node.animate) node.animate(
      [{opacity:0, clipPath:'inset(0 0 100% 0)',transform:'translateY(10px)'}, {opacity:1,clipPath:'inset(0)',transform:'translateY(0)'}],
      {duration:650, easing:'steps(10,end)'});
  };
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        animateIn(entry.target); observer.unobserve(entry.target);
      }
    }, {threshold:.1});
    document.querySelectorAll('[data-reveal]').forEach(node => observer.observe(node));
  }
  reduced.addEventListener('change', () => {
    if(reduced.matches) document.getAnimations().forEach(animation => animation.finish());
  });
  const agents = {
    codex:{path:'.agents/skills/android-device-care/', note:'Codex discovers project skills in .agents/skills. Start a new chat if the skill doesn’t appear.'},
    cursor:{path:'.cursor/skills/android-device-care/', note:'Cursor discovers project skills in .cursor/skills. Use / in Agent chat to find the skill.'},
    claude:{path:'.claude/skills/android-device-care/', note:'Claude Code discovers project skills in .claude/skills. Invoke /android-device-care in a local session.'},
    antigravity:{path:'.agents/skills/android-device-care/', note:'Current Antigravity IDE uses .agents/skills. Inspect the skill in the agent side panel’s Customizations menu.'}
  };
  const tabs = [...document.querySelectorAll('[data-agent]')];
  const panel = document.getElementById('install-panel');
  function select(tab) {
    const agent = agents[tab.dataset.agent];
    tabs.forEach(item => {const active=item===tab; item.setAttribute('aria-selected',String(active));item.tabIndex=active?0:-1;});
    const runtime=document.getElementById('python-command').value;
    document.getElementById('skill-path').textContent='git clone https://github.com/HemantKumar822/debloat-android.git debloat-android\n'+runtime+' debloat-android/scripts/install_skill.py --agent '+tab.dataset.agent+' --user';
    document.getElementById('agent-note').textContent=agent.note;
    document.getElementById('copy-feedback').textContent='';
    panel.setAttribute('aria-labelledby',tab.id);
  }
  document.getElementById('python-command')?.addEventListener('change',()=>select(tabs.find(t=>t.getAttribute('aria-selected')==='true')));
  tabs.forEach((tab,index) => {
    tab.addEventListener('click',()=>select(tab));
    tab.addEventListener('keydown',event=>{
      let next;
      if(event.key==='ArrowRight') next=(index+1)%tabs.length;
      if(event.key==='ArrowLeft') next=(index+tabs.length-1)%tabs.length;
      if(event.key==='Home') next=0;
      if(event.key==='End') next=tabs.length-1;
      if(next!==undefined){event.preventDefault();select(tabs[next]);tabs[next].focus();}
    });
  });
  async function copy(id,label) {
    const text=document.getElementById(id).textContent;
    const feedback=document.getElementById('copy-feedback');
    try {await navigator.clipboard.writeText(text);feedback.textContent=label+' copied.';}
    catch {feedback.textContent='Clipboard unavailable. Select the text above and copy it manually.';}
  }
  document.getElementById('copy-path')?.addEventListener('click',()=>copy('skill-path','Installation commands'));
  document.getElementById('copy-prompt')?.addEventListener('click',()=>copy('skill-prompt','Agent prompt'));
})();
