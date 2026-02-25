(function(){
  // Simple renderer for Onigiri-style sidebar buttons.
  const buttons = [
    { id: 'browse', label: 'Browse', action: () => window.location.href = '/' },
    { id: 'stats', label: 'Stats', action: () => window.location.href = '/stats' },
    { id: 'decks', label: 'Decks', action: () => window.location.href = '/' },
    { id: 'settings', label: 'Settings', action: () => window.location.href = '/settings' }
  ];

  function makeSvgIcon(id){
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'sidebar-button-icon');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'currentColor');
    
    const iconMap = {
      browse: '<circle cx="12" cy="12" r="10" stroke="currentColor" fill="none" stroke-width="2"/>',
      stats: '<rect x="2" y="8" width="4" height="12" stroke="currentColor" fill="none" stroke-width="2"/><rect x="10" y="4" width="4" height="16" stroke="currentColor" fill="none" stroke-width="2"/><rect x="18" y="6" width="4" height="14" stroke="currentColor" fill="none" stroke-width="2"/>',
      decks: '<rect x="2" y="2" width="8" height="8" stroke="currentColor" fill="none" stroke-width="2"/><rect x="14" y="2" width="8" height="8" stroke="currentColor" fill="none" stroke-width="2"/><rect x="2" y="14" width="8" height="8" stroke="currentColor" fill="none" stroke-width="2"/><rect x="14" y="14" width="8" height="8" stroke="currentColor" fill="none" stroke-width="2"/>',
      settings: '<circle cx="12" cy="12" r="3" stroke="currentColor" fill="none" stroke-width="2"/><circle cx="12" cy="12" r="9" stroke="currentColor" fill="none" stroke-width="1.5"/>'
    };
    svg.innerHTML = iconMap[id] || '<circle cx="12" cy="12" r="10" stroke="currentColor" fill="none" stroke-width="2"/>';
    return svg;
  }

  function makeButton(b){
    const a = document.createElement('a');
    a.className = 'sidebar-button';
    a.href = '#';
    a.dataset.id = b.id;
    a.onclick = (e)=>{ e.preventDefault(); b.action(); };

    const icon = makeSvgIcon(b.id);
    const label = document.createElement('span'); label.className = 'label'; label.textContent = b.label;
    a.appendChild(icon); a.appendChild(label);
    return a;
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    const container = document.getElementById('sidebar-buttons');
    if(!container) return;
    buttons.forEach(b=> container.appendChild(makeButton(b)));

    // Submit logout when logout button is clicked
    const logoutBtn = document.getElementById('sidebar-logout-btn');
    if(logoutBtn){
      logoutBtn.addEventListener('click', (e)=>{
        e.preventDefault();
        const logoutForm = document.getElementById('logout-form');
        if(logoutForm) logoutForm.submit();
      });
    }

    // If sidebar static links exist in template, copy their hrefs to the sidebar links (keeps urls centralized)
    const donateSrc = document.getElementById('donate-link');
    if(donateSrc){
      const sideDonate = document.getElementById('sidebar-donate');
      if(sideDonate) sideDonate.href = donateSrc.href;
    }
    const aboutSrc = document.getElementById('about-link');
    if(aboutSrc){
      const sideAbout = document.getElementById('sidebar-about');
      if(sideAbout) sideAbout.href = aboutSrc.href;
    }
    const contactSrc = document.getElementById('contact-link');
    if(contactSrc){
      const sideContact = document.getElementById('sidebar-contact');
      if(sideContact) sideContact.href = contactSrc.href;
    }
  });
})();
