(function() {
  'use strict';
  const header = document.querySelector('.site-header');
  const hero = document.querySelector('.hero');
  if (header && hero) {
    new IntersectionObserver(function([entry]) {
      header.classList.toggle('scrolled', !entry.isIntersecting);
    }, { rootMargin: '-100px 0px 0px 0px' }).observe(hero);
  }

  let returnFocus = null;
  const menuToggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#mobile-menu');
  function openDialog(dialog, trigger) {
    if (!dialog) return;
    returnFocus = trigger || document.activeElement;
    dialog.showModal();
    document.body.classList.add('modal-open');
  }
  document.querySelectorAll('dialog').forEach(function(dialog) {
    dialog.addEventListener('keydown', function(event) {
      if (event.key !== 'Tab') return;
      const focusable = Array.prototype.slice.call(dialog.querySelectorAll('a[href],button,input,select,textarea,[tabindex]'))
        .filter(function(el) {
          return !el.disabled && el.tabIndex >= 0 && el.getClientRects().length;
        });
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (!first) { event.preventDefault(); return; }
      if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    });
    dialog.querySelectorAll('[data-close]').forEach(function(button) {
      button.addEventListener('click', function() {
        dialog.close();
      });
    });
    dialog.addEventListener('click', function(event) {
      const r = dialog.getBoundingClientRect();
      if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) dialog.close();
    });
    dialog.addEventListener('close', function() {
      document.body.classList.remove('modal-open');
      if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
      if (returnFocus) returnFocus.focus({ preventScroll: true });
    });
  });
  if (menuToggle) {
    menuToggle.addEventListener('click', function() {
      openDialog(menu, menuToggle);
      menuToggle.setAttribute('aria-expanded', 'true');
    });
  }
  if (menu) {
    menu.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        menu.close();
      });
    });
  }
  window.addEventListener('resize', function() {
    if (window.innerWidth > 900 && menu && menu.open) menu.close();
  });

  const tabs = Array.prototype.slice.call(document.querySelectorAll('[role="tab"]'));
  function selectTab(tab) {
    tabs.forEach(function(t) {
      const active = tab === t;
      t.setAttribute('aria-selected', String(active));
      t.tabIndex = active ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !active;
    });
  }
  tabs.forEach(function(tab, index) {
    tab.addEventListener('click', function() {
      selectTab(tab);
    });
    tab.addEventListener('keydown', function(event) {
      let next = index;
      if (['ArrowDown', 'ArrowRight'].includes(event.key)) next = (index + 1) % tabs.length;
      else if (['ArrowUp', 'ArrowLeft'].includes(event.key)) next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault();
      selectTab(tabs[next]);
      tabs[next].focus();
    });
  });
  const tabList = document.querySelector('[role="tablist"]');
  const horizontalTabs = matchMedia('(max-width:900px)');
  const orientTabs = function() {
    if (tabList) tabList.setAttribute('aria-orientation', horizontalTabs.matches ? 'horizontal' : 'vertical');
  };
  orientTabs();
  horizontalTabs.addEventListener('change', orientTabs);

  const filterPanel = document.querySelector('.filter-panel');
  const filterDialog = document.querySelector('.filter-dialog');
  const filterToggle = document.querySelector('[data-filter-open]');
  const filterForm = filterPanel && filterPanel.querySelector('form');
  if (filterPanel && filterDialog && filterToggle && filterForm) {
    filterPanel.classList.add('enhanced');
    filterToggle.classList.add('enhanced');
    filterToggle.addEventListener('click', function() {
      filterDialog.append(filterForm);
      openDialog(filterDialog, filterToggle);
    });
    filterDialog.addEventListener('close', function() {
      filterPanel.append(filterForm);
    });
    window.addEventListener('resize', function() {
      if (window.innerWidth > 768 && filterDialog.open) filterDialog.close();
    });
  }

  const drawer = document.querySelector('#enquiry');
  const form = document.querySelector('#enquiry-form');
  if (!form) return;
  const success = document.querySelector('.enquiry-success');
  const status = document.querySelector('.form-status');
  const errors = document.querySelector('#form-errors');
  let submitting = false;
  let lastTokenAt = Date.now();
  async function refreshToken() {
    const response = await fetch('/enquiry/token/', { credentials: 'same-origin', cache: 'no-store' });
    if (!response.ok) throw new Error('Unable to start a secure enquiry. Please reload the page.');
    const data = await response.json();
    form.elements.token.value = data.token; lastTokenAt = Date.now();
  }
  document.querySelectorAll('[data-enquire]').forEach(function(trigger) {
    trigger.addEventListener('click', async function(event) {
      event.preventDefault();
      if (success.hidden === false) { form.reset(); form.hidden = false; success.hidden = true; lastTokenAt = 0; }
      if (trigger.dataset.interest && !form.elements.message.value) form.elements.message.value = 'I would like to discuss ' + trigger.dataset.interest.toLowerCase() + '.';
      openDialog(drawer, trigger);
      if (Date.now() - lastTokenAt > 50 * 60 * 1000) {
        try {
          await refreshToken();
        } catch (error) {
          errors.textContent = error.message;
        }
      }
    });
  });
  if (drawer && drawer.dataset.errors === 'true') openDialog(drawer);
  form.addEventListener('submit', async function(event) {
    event.preventDefault();
    if (submitting || !form.reportValidity()) return;
    submitting = true;
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true; form.setAttribute('aria-busy', 'true');
    status.textContent = 'Sending your enquiry…'; errors.replaceChildren();
    form.querySelectorAll('.field-error').forEach(function(el) {
      el.textContent = '';
    });
    form.querySelectorAll('[aria-invalid]').forEach(function(el) {
      el.removeAttribute('aria-invalid');
      el.removeAttribute('aria-describedby');
    });
    try {
      const response = await fetch(form.action, { method: 'POST', body: new FormData(form), credentials: 'same-origin', headers: { 'Accept': 'application/json' }, signal: AbortSignal.timeout(20000) });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        let firstInvalid;
        Object.entries(data.errors || {}).forEach(function([key, values]) {
          const message = values.map(function(v) {
            return v.message;
          }).join(' ');
          const field = form.elements[key];
          const target = document.getElementById('error-' + key);
          if (field && target) {
            target.textContent = message;
            field.setAttribute('aria-invalid', 'true');
            field.setAttribute('aria-describedby', target.id);
            firstInvalid = firstInvalid || field;
          } else {
            const p = document.createElement('p');
            p.textContent = message;
            errors.append(p);
          }
        });
        if (!errors.textContent) errors.textContent = 'Please check the highlighted fields.';
        (firstInvalid || errors).focus();
        status.textContent = '';
      } else {
        form.hidden = true;
        success.hidden = false;
        success.focus();
        status.textContent = '';
      }
    } catch (_) {
      errors.textContent = 'We could not confirm receipt. Please try again or contact info@ncctdxb.com. Your details are still here.';
      errors.focus();
      status.textContent = '';
    } finally {
      submitting = false;
      submit.disabled = false;
      form.removeAttribute('aria-busy');
    }
  });
})();
