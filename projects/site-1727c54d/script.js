document.getElementById('eventForm')?.addEventListener('submit', (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.currentTarget).entries());
  const status = document.getElementById('status');
  status.textContent = 'Submitting...';
  setTimeout(() => {
    status.textContent = '✅ Submitted! ' + JSON.stringify(data);
    e.currentTarget.reset();
  }, 600);
});