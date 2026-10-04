// Keep the native admin table and controls, with readable stacked rows on phones.
document.addEventListener('DOMContentLoaded', () => {
  const table = document.querySelector('#result_list');
  if (!table) return;
  const labels = [...table.querySelectorAll('thead th')].map(cell =>
    (cell.querySelector('.text') || cell).textContent.trim());
  table.querySelectorAll('tbody tr').forEach(row => {
    [...row.children].forEach((cell, index) => {
      if (index > 0) cell.dataset.label = labels[index] || '';
    });
  });
});
