// NCCT admin interactions: navigation drawer, file pickers, loading states.
(function () {
  var body = document.body;
  var KEY = 'ncct-admin-nav';
  var mobile = function () { return window.matchMedia('(max-width: 900px)').matches; };
  document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.querySelector('[data-nav-toggle]');
    var scrim = document.querySelector('.scrim');
    if (toggle) {
      if (!mobile() && localStorage.getItem(KEY) === 'collapsed') body.classList.add('nav-collapsed');
      var sync = function () {
        toggle.setAttribute('aria-expanded', mobile() ? body.classList.contains('nav-open') : !body.classList.contains('nav-collapsed'));
        if (scrim) scrim.hidden = !body.classList.contains('nav-open');
      };
      toggle.addEventListener('click', function () {
        if (mobile()) body.classList.toggle('nav-open');
        else {
          body.classList.toggle('nav-collapsed');
          localStorage.setItem(KEY, body.classList.contains('nav-collapsed') ? 'collapsed' : 'open');
        }
        sync();
      });
      document.querySelectorAll('[data-nav-close]').forEach(function (el) {
        el.addEventListener('click', function () { body.classList.remove('nav-open'); sync(); });
      });
      document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape') return;
        body.classList.remove('nav-open');
        sync();
        document.querySelectorAll('.usermenu[open]').forEach(function (d) { d.open = false; });
      });
      window.addEventListener('resize', function () { if (!mobile()) body.classList.remove('nav-open'); sync(); });
      sync();
    }
    document.addEventListener('click', function (e) {
      document.querySelectorAll('.usermenu[open]').forEach(function (d) { if (!d.contains(e.target)) d.open = false; });
    });
    // Show the chosen file name next to the upload button.
    document.addEventListener('change', function (e) {
      var input = e.target;
      if (input.type !== 'file') return;
      var pick = input.closest('.file-pick');
      var label = pick && pick.querySelector('.file-name');
      if (label) label.textContent = input.files.length ? input.files[0].name + ' (saved when you submit)' : 'No new file selected';
    });
    // Keep the filter panel compact on small screens.
    if (mobile()) document.querySelectorAll('#changelist-filter details').forEach(function (d) { d.open = false; });
    // Changelist: label cells for the stacked mobile layout.
    var table = document.querySelector('#result_list');
    if (table) {
      var labels = Array.prototype.map.call(table.querySelectorAll('thead th'), function (c) {
        return ((c.querySelector('.text') || c).textContent || '').trim();
      });
      table.querySelectorAll('tbody tr').forEach(function (row) {
        Array.prototype.forEach.call(row.children, function (cell, i) { if (i > 0) cell.dataset.label = labels[i] || ''; });
      });
    }
    // Loading feedback on save without disabling the submit button (its value must be posted).
    document.querySelectorAll('form').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        if (e.defaultPrevented) return;
        if (form.dataset.busy) { e.preventDefault(); return; }
        form.dataset.busy = '1';
        var s = e.submitter;
        if (s && s.classList) s.classList.add('is-loading');
        setTimeout(function () { delete form.dataset.busy; if (s && s.classList) s.classList.remove('is-loading'); }, 15000);
      });
    });
  });
  // Confirm bulk actions that change what visitors see.
  document.addEventListener('submit', function (event) {
    var form = event.target;
    var select = form.querySelector && form.querySelector('select[name="action"]');
    if (!select || !select.value || select.value === 'delete_selected') return;
    if (/unpublish|remove|closed/.test(select.value) &&
        !window.confirm('Apply "' + select.options[select.selectedIndex].text + '" to the selected items? This changes what visitors see on the website.')) {
      event.preventDefault();
    }
  });
  // Confirm removal of gallery rows or files.
  document.addEventListener('change', function (e) {
    var el = e.target;
    if (el.type === 'checkbox' && el.checked && (/-DELETE$/.test(el.name) || /-clear$/.test(el.name)) &&
        !window.confirm('Remove this item? It is deleted only when you save the page.')) {
      el.checked = false;
    }
  });
})();
