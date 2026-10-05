document.addEventListener('DOMContentLoaded', () => {
  const links = [...document.querySelectorAll('[data-lightbox]')];
  if (!links.length) return;
  const box = document.createElement('dialog');
  box.className = 'lightbox';
  box.setAttribute('aria-label', 'Image viewer');
  box.innerHTML = '<button type="button" aria-label="Close image">×</button>';
  document.body.append(box);
  const img = document.createElement('img');
  links.forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    if (!img.isConnected) box.append(img);
    img.src = link.href;
    img.alt = link.dataset.lightbox || '';
    box.showModal();
  }));
  box.addEventListener('click', () => box.close());
});
document.addEventListener('DOMContentLoaded', () => {
  const list = document.querySelector('.category-nav ul');
  if (!list) return;
  const prev = document.querySelector('.cat-prev');
  const next = document.querySelector('.cat-next');
  const update = () => {
    const max = list.scrollWidth - list.clientWidth;
    prev.hidden = list.scrollLeft <= 2;
    next.hidden = max <= 2 || list.scrollLeft >= max - 2;
  };
  const step = dir => list.scrollBy({ left: dir * Math.max(160, list.clientWidth * 0.7), behavior: 'smooth' });
  prev.addEventListener('click', () => step(-1));
  next.addEventListener('click', () => step(1));
  list.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  const active = list.querySelector('.is-active');
  if (active) {
    list.style.scrollBehavior = 'auto';
    list.scrollLeft = Math.max(0, active.offsetLeft - (list.clientWidth - active.offsetWidth) / 2);
    list.style.scrollBehavior = '';
  }
  update();
});