/* Progressive enhancement: a native gallery first, a scroll-linked gallery when suitable. */
(() => {
  'use strict';
  // Safe if this file is evaluated again by a development/navigation integration.
  window.ncctLightingGallery?.destroy();
  const instances = [...document.querySelectorAll('[data-lighting-gallery]')].map(createGallery);
  window.ncctLightingGallery = {destroy() { instances.forEach(instance => instance.destroy()); }};

  function createGallery(root) {
    const runway = root.querySelector('.moments-runway');
    const pin = root.querySelector('.moments-pin');
    const viewport = root.querySelector('.moments-viewport');
    const track = root.querySelector('.moments-track');
    const cards = [...root.querySelectorAll('.moment-card')];
    const hint = root.querySelector('.moments-hint');
    const index = root.querySelector('.moments-index');
    const media = matchMedia('(min-width:768px) and (min-height:600px) and (prefers-reduced-motion:no-preference)');
    const reduced = matchMedia('(prefers-reduced-motion:reduce)');
    const listeners = new AbortController();
    const {signal} = listeners;
    const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
    let enhanced = false, travel = 0, width = 0, centers = [], position = 0;
    let frame = 0, resizeFrame = 0, lastTime = 0, active = -1, destroyed = false;

    function updateIndex(next, progress) {
      if (active !== next) {
        active = next;
        cards.forEach((card, i) => card.toggleAttribute('data-active', i === next));
        index.firstChild.textContent = `${String(next + 1).padStart(2, '0')} `;
      }
      root.style.setProperty('--moment-progress', String(progress));
    }

    function paint(x) {
      let nearest = 0, distance = Infinity;
      if (enhanced) track.style.transform = `translate3d(${-x}px,0,0)`;
      centers.forEach((center, i) => {
        const delta = center - x - width / 2;
        if (Math.abs(delta) < distance) { nearest = i; distance = Math.abs(delta); }
        if (enhanced || (!reduced.matches && width < 768)) {
          const relative = clamp(delta / (width / 2), -1, 1);
          const edge = Math.abs(relative);
          const mobileArc = !enhanced;
          const angle = mobileArc ? 7 : (width < 1050 ? 10 : 16);
          cards[i].style.transform = `perspective(1200px) translateY(${mobileArc ? edge * edge * 28 : edge * 12}px) rotateY(${-relative * angle}deg) scale(${1 - edge * (mobileArc ? .085 : .045)})`;
        } else {
          cards[i].style.removeProperty('transform');
        }
      });
      updateIndex(nearest, (1 + (cards.length - 1) * (travel ? x / travel : 0)) / cards.length);
    }

    function render(time) {
      frame = 0;
      if (destroyed) return;
      if (!enhanced) { paint(viewport.scrollLeft); return; }
      // One layout read, then transform-only writes. No wheel or touch interception.
      const top = runway.getBoundingClientRect().top;
      const target = clamp(92 - top, 0, travel);
      const deltaTime = lastTime ? Math.min(time - lastTime, 64) : 16;
      lastTime = time;
      const outside = top > innerHeight || top + pin.offsetHeight + travel < 0;
      if (outside && position === target) { lastTime = 0; return; }
      position = outside ? target : position + (target - position) * (1 - Math.exp(-deltaTime / 65));
      if (Math.abs(target - position) < .15) position = target;
      paint(position);
      if (position !== target) frame = requestAnimationFrame(render);
      else lastTime = 0;
    }

    function schedule() {
      if (!frame && !destroyed) frame = requestAnimationFrame(render);
    }

    function measure() {
      resizeFrame = 0;
      if (destroyed) return;
      width = viewport.clientWidth;
      // offsetLeft is unaffected by perspective, unlike getBoundingClientRect().
      centers = cards.map(card => card.offsetLeft - track.offsetLeft + card.offsetWidth / 2);
      travel = Math.max(0, track.scrollWidth - width);
      const shouldEnhance = media.matches && travel > 0;
      if (enhanced !== shouldEnhance) {
        enhanced = shouldEnhance;
        root.classList.toggle('is-scroll-gallery', enhanced);
        track.style.removeProperty('transform');
        cards.forEach(card => card.style.removeProperty('transform'));
        viewport.scrollLeft = 0;
      }
      if (enhanced) {
        root.style.setProperty('--moment-runway', `${pin.offsetHeight + travel}px`);
        position = clamp(92 - runway.getBoundingClientRect().top, 0, travel);
        hint.textContent = 'Scroll to discover';
      } else {
        root.style.removeProperty('--moment-runway');
        hint.textContent = 'Swipe or scroll to explore';
      }
      paint(enhanced ? position : viewport.scrollLeft);
      schedule();
    }

    function requestMeasure() {
      if (!resizeFrame && !destroyed) resizeFrame = requestAnimationFrame(measure);
    }

    // Tabbing to a card brings that link into the visual viewport, including when pinned.
    track.addEventListener('focusin', event => {
      if (!enhanced) return;
      const card = event.target.closest('.moment-card');
      const i = cards.indexOf(card);
      if (i < 0) return;
      const x = clamp(centers[i] - width / 2, 0, travel);
      const start = runway.getBoundingClientRect().top + scrollY - 92;
      position = x;
      window.scrollTo({top: start + x, behavior: 'instant'});
      paint(x);
    }, {signal});

    window.addEventListener('scroll', schedule, {passive: true, signal});
    viewport.addEventListener('scroll', schedule, {passive: true, signal});
    window.addEventListener('resize', requestMeasure, {passive: true, signal});
    window.addEventListener('pageshow', requestMeasure, {signal});
    window.addEventListener('pagehide', () => { cancelAnimationFrame(frame); frame = 0; lastTime = 0; }, {signal});
    media.addEventListener('change', requestMeasure, {signal});
    reduced.addEventListener('change', requestMeasure, {signal});
    const observer = new ResizeObserver(requestMeasure);
    observer.observe(viewport);
    cards.forEach(card => {
      const img = card.querySelector('img');
      if (!img.complete) img.addEventListener('load', requestMeasure, {once: true, signal});
    });
    document.fonts?.ready.then(() => { if (!destroyed) requestMeasure(); });

    measure();
    return {destroy() {
      destroyed = true;
      listeners.abort();
      observer.disconnect();
      cancelAnimationFrame(frame);
      cancelAnimationFrame(resizeFrame);
      root.classList.remove('is-scroll-gallery');
      root.style.removeProperty('--moment-runway');
      root.style.removeProperty('--moment-progress');
      track.style.removeProperty('transform');
      cards.forEach(card => { card.style.removeProperty('transform'); card.removeAttribute('data-active'); });
    }};
  }
})();
