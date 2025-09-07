// Small interactive behaviors: expand item details and demo hooks
document.addEventListener('DOMContentLoaded', function(){
  // Expand/collapse details when the entire item is clicked (but keep links/buttons functional)
  document.querySelectorAll('.about-item').forEach(function(item){
    item.addEventListener('click', function(e){
      // avoid toggling when clicking interactive controls inside
      if(e.target.tagName.toLowerCase() === 'button' || e.target.closest('.btn')) return;
      item.classList.toggle('open');
    });
  });

  // Hook up demo & brief buttons (mock behavior)
  var demoBtn = document.getElementById('demo-btn');
  var briefBtn = document.getElementById('brief-btn');
  demoBtn && demoBtn.addEventListener('click', function(){
    // This is intentionally a mock: integrate your GIS/map here (Leaflet/Mapbox/GoogleMaps)
    alert('Demo opened — integrate map/GIS here (replace the map placeholder with your map container).');
  });
  briefBtn && briefBtn.addEventListener('click', function(){
    // Simple downloadable brief generator (client-side). For production, provide server-side PDF.
    var text = 'SIH 2025 — RTRWH & AR brief\n\nProject: On-spot assessment of rooftop rainwater harvesting and artificial recharge.\n\nKey points:\n';
    document.querySelectorAll('.about-list .about-item h3').forEach(function(h){text += '- ' + h.textContent + '\n';});
    var blob = new Blob([text], {type: 'text/plain'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'SIH2025_RTRWH_brief.txt'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  });

  // Accessibility: allow keyboard to expand/collapse
  document.addEventListener('keydown', function(e){
    if(e.key === 'Enter' || e.key === ' '){
      var focused = document.activeElement;
      if(focused && focused.closest && focused.closest('.about-item')){
        focused.closest('.about-item').classList.toggle('open');
        e.preventDefault();
      }
    }
  });
});
