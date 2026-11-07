(() => {
  'use strict';

  document.querySelectorAll('[data-about-project-slider]').forEach(root => {
    const viewport = root.querySelector('[data-slider-viewport]');
    const track = root.querySelector('[data-slider-track]');
    const slides = [...root.querySelectorAll('[data-slider-slide]')];
    const currentLabel = root.querySelector('[data-slider-current]');
    const progress = root.querySelector('[data-slider-progress]');
    const progressFill = root.querySelector('[data-slider-progress-fill]');
    const previous = root.querySelector('[data-slider-prev]');
    const next = root.querySelector('[data-slider-next]');
    const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
    const controller = new AbortController();
    const {signal} = controller;
    let step = 0;
    let centers = [];
    let minOffset = 0;
    let maxOffset = 0;
    let offset = 0;
    let active = 0;
    let pointer = null;
    let moved = false;
    let suppressClick = false;
    let settleTimer = 0;
    let destroyed = false;

    if (!viewport || !track || !slides.length || !currentLabel || !progress || !progressFill || !previous || !next) return;

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function updateControls(index) {
      active = clamp(index, 0, slides.length - 1);
      currentLabel.textContent = String(active + 1).padStart(2, '0');
      progress.setAttribute('aria-valuenow', String(active + 1));
      progressFill.style.transform = `scaleX(${(active + 1) / slides.length})`;
      previous.disabled = active === 0;
      next.disabled = active === slides.length - 1;
    }

    function paint(value) {
      offset = clamp(value, minOffset, maxOffset);
      track.style.transform = `translate3d(${-offset}px,0,0)`;
      const viewportCenter = offset + viewport.clientWidth / 2;
      let nearest = 0;
      let nearestDistance = Infinity;
      slides.forEach((slide, index) => {
        const distance = centers[index] - viewportCenter;
        const absoluteDistance = Math.abs(distance);
        if (absoluteDistance < nearestDistance) {
          nearest = index;
          nearestDistance = absoluteDistance;
        }

        const relative = step ? distance / step : 0;
        const arcDistance = Math.min(Math.abs(relative), 2);
        const verticalOffset = -8 + arcDistance * 19;
        const scale = 1 - arcDistance * 0.075;
        const rotation = Math.sign(relative) * arcDistance * 1.1;
        slide.style.transform = `translate3d(0,${verticalOffset}px,0) rotate(${rotation}deg) scale(${scale})`;
        slide.style.zIndex = String(10 - Math.round(arcDistance * 2));
      });
      updateControls(nearest);
    }

    function snapTo(index) {
      const target = clamp(index, 0, slides.length - 1);
      root.classList.add('is-settling');
      paint(centers[target] - viewport.clientWidth / 2);
      window.clearTimeout(settleTimer);
      settleTimer = window.setTimeout(() => root.classList.remove('is-settling'), reducedMotion.matches ? 0 : 560);
    }

    function measure() {
      if (destroyed) return;
      const previousIndex = active;
      centers = slides.map(slide => slide.offsetLeft + slide.offsetWidth / 2);
      step = centers[1] ? centers[1] - centers[0] : 0;
      minOffset = centers[0] - viewport.clientWidth / 2;
      maxOffset = centers[centers.length - 1] - viewport.clientWidth / 2;
      root.classList.add('is-ready');
      paint(centers[previousIndex] - viewport.clientWidth / 2);
    }

    function onPointerDown(event) {
      if (event.button !== 0 || !event.isPrimary) return;
      pointer = {
        id: event.pointerId,
        startX: event.clientX,
        startOffset: offset,
        lastX: event.clientX,
        lastTime: performance.now(),
        velocity: 0
      };
      moved = false;
      root.classList.remove('is-settling');
      window.clearTimeout(settleTimer);
      viewport.setPointerCapture(event.pointerId);
    }

    function onPointerMove(event) {
      if (!pointer || event.pointerId !== pointer.id) return;
      const deltaX = event.clientX - pointer.startX;
      if (Math.abs(deltaX) > 5) {
        moved = true;
        root.classList.add('is-dragging');
      }
      if (!moved) return;
      const now = performance.now();
      const elapsed = Math.max(1, now - pointer.lastTime);
      const nextOffset = clamp(pointer.startOffset - deltaX, minOffset, maxOffset);
      pointer.velocity = (nextOffset - offset) / elapsed;
      pointer.lastX = event.clientX;
      pointer.lastTime = now;
      paint(nextOffset);
    }

    function onPointerUp(event) {
      if (!pointer || event.pointerId !== pointer.id) return;
      const velocity = pointer.velocity;
      pointer = null;
      root.classList.remove('is-dragging');
      if (moved) {
        suppressClick = true;
        window.setTimeout(() => { suppressClick = false; }, 250);
        const momentum = clamp(velocity * 150, -step * .35, step * .35);
        const projected = reducedMotion.matches ? offset : offset + momentum;
        let nearest = active;
        let nearestDistance = Infinity;
        centers.forEach((center, index) => {
          const distance = Math.abs(center - (projected + viewport.clientWidth / 2));
          if (distance < nearestDistance) {
            nearest = index;
            nearestDistance = distance;
          }
        });
        snapTo(nearest);
      } else {
        snapTo(active);
      }
    }

    function onPointerCancel(event) {
      if (!pointer || event.pointerId !== pointer.id) return;
      pointer = null;
      root.classList.remove('is-dragging');
      snapTo(active);
    }

    viewport.addEventListener('pointerdown', onPointerDown, {signal});
    viewport.addEventListener('pointermove', onPointerMove, {signal});
    viewport.addEventListener('pointerup', onPointerUp, {signal});
    viewport.addEventListener('pointercancel', onPointerCancel, {signal});
    viewport.addEventListener('lostpointercapture', onPointerCancel, {signal});
    viewport.addEventListener('click', event => {
      if (!suppressClick) return;
      event.preventDefault();
      event.stopPropagation();
      suppressClick = false;
    }, {capture: true, signal});
    viewport.addEventListener('dragstart', event => event.preventDefault(), {signal});
    viewport.addEventListener('keydown', event => {
      if (event.target !== viewport) return;
      if (event.key === 'ArrowLeft' && active > 0) {
        event.preventDefault();
        snapTo(active - 1);
      } else if (event.key === 'ArrowRight' && active < slides.length - 1) {
        event.preventDefault();
        snapTo(active + 1);
      }
    }, {signal});
    track.addEventListener('focusin', event => {
      const slide = event.target.closest('[data-slider-slide]');
      const index = slides.indexOf(slide);
      if (index >= 0 && index !== active) snapTo(index);
    }, {signal});
    previous.addEventListener('click', () => snapTo(active - 1), {signal});
    next.addEventListener('click', () => snapTo(active + 1), {signal});

    const observer = new ResizeObserver(measure);
    observer.observe(viewport);
    slides.forEach(slide => {
      const image = slide.querySelector('img');
      if (image && !image.complete) image.addEventListener('load', measure, {once: true, signal});
    });
    measure();

    root.addEventListener('DOMNodeRemoved', event => {
      if (event.target !== root) return;
      destroyed = true;
      observer.disconnect();
      controller.abort();
      window.clearTimeout(settleTimer);
    }, {once: true});
  });
})();
