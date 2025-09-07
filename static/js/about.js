// static/js/about.js
// Lightweight raindrop generator for the About section.
// Save as: static/js/about.js

document.addEventListener('DOMContentLoaded', function () {
  // existing interactive code: expand items and demo/brief buttons
  document.querySelectorAll('.about-item').forEach(function(item){
    item.addEventListener('click', function(e){
      if (e.target.tagName.toLowerCase() === 'button' || e.target.closest('.btn')) return;
      item.classList.toggle('open');
    });
  });

  var demoBtn = document.getElementById('demo-btn');
  var briefBtn = document.getElementById('brief-btn');
  demoBtn && demoBtn.addEventListener('click', function(){ alert('Demo opened — integrate map/GIS here.'); });
  briefBtn && briefBtn.addEventListener('click', function(){
    var text = 'SIH 2025 — RTRWH & AR brief\n\nProject: On-spot assessment of rooftop rainwater harvesting and artificial recharge.\n\nKey points:\n';
    document.querySelectorAll('.about-list .about-item h3').forEach(function(h){ text += '- ' + h.textContent + '\n'; });
    var blob = new Blob([text], {type: 'text/plain'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'SIH2025_RTRWH_brief.txt'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  });

  // -------------------------
  // Raindrop generation
  // -------------------------
  var section = document.querySelector('.about-section');
  if (!section) return;

  // create rain container if not present
  var rain = section.querySelector('.rain');
  if (!rain) {
    rain = document.createElement('div');
    rain.className = 'rain';
    section.insertBefore(rain, section.firstChild); // behind content but above bg-clouds (z-index controlled in CSS)
  }

  // parameters
  var dropCount = 28; // tweak for performance
  var sectionWidth = section.offsetWidth || window.innerWidth;

  function rand(min, max) { return Math.random() * (max - min) + min; }

  // create drops
  for (var i = 0; i < dropCount; i++) {
    (function(i){
      var drop = document.createElement('div');
      drop.className = 'raindrop';

      // randomize start left (0-100%), slight negative allowed for overflow
      var left = rand(-8, 108);
      drop.style.left = left + '%';

      // randomize width and height (gives variety)
      var widthPx = rand(1, 3);
      var heightVh = rand(8, 18);
      drop.style.width = widthPx + 'px';
      drop.style.height = heightVh + 'vh';

      // randomize fall duration and delay
      var duration = rand(1.2, 2.6); // seconds
      var delay = rand(-2.0, 0.8); // negative delays to stagger initial appearance

      // horizontal drift via transform animation (implemented with CSS animation generated per element)
      // create keyframes for this element by injecting animation through style attribute
      var animName = 'fallAnim' + i;
      var styleEl = document.createElement('style');
      styleEl.innerHTML = "\n@keyframes " + animName + " {\n" +
        "0% { transform: translateY(-20vh) translateX(0) scaleY(0.9); opacity: 0.95; }\n" +
        "70% { opacity: 0.95; }\n" +
        "90% { opacity: 0.35; }\n" +
        "100% { transform: translateY(110vh) translateX(" + (rand(-8,8)) + "vw) scaleY(1); opacity: 0; }\n" +
      "}\n";
      document.head.appendChild(styleEl);

      drop.style.animation = animName + ' ' + duration + 's linear ' + delay + 's infinite';
      // randomize opacity slightly
      drop.style.opacity = rand(0.6, 0.95);

      // optional staggered blur/scale
      drop.style.transformOrigin = 'top center';

      rain.appendChild(drop);

      // remove style tag later on unload if desired (not necessary)
    })(i);
  }

  // handle resize: optionally remove & re-create drops (kept simple here)
  window.addEventListener('resize', function(){
    // a quick, cheap strategy: if width changed significantly, clear and recreate a smaller set
    // (left as a no-op to keep code minimal; update if you notice visual glitches).
  }, { passive: true });

});
