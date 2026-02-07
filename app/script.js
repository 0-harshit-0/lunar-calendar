// initial load
(async function init() {
  // copy coordinates buttons
  document.querySelectorAll('.copy-coords').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const target = e.currentTarget.dataset.target;
      let text = '';
      if (target === 'sun') text = sunXYZPre.textContent;
      if (target === 'moon') text = moonXYZPre.textContent;
      try {
        await navigator.clipboard.writeText(text);
        setStatus('Coordinates copied');
      } catch (err) {
        setStatus('Could not copy coordinates: ' + err.message, true);
      }
    });
  });

  // form submit handler
  dateForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const iso = dateInput.value;
    if (!iso) {
      setStatus('Please choose a date', true);
      return;
    }
    const data = await fetchForDate(iso);
    canvasDraw(data);
  });

  calendarCanvas.addEventListener('dblclick', async (e) => {
    const iso = dateInput.value;
    if (!iso) {
      setStatus('Please choose a date', true);
      return;
    }
    const data = await fetchPlanetsForDate(iso);
    openSpace();
    planetsDraw(data);
  });

  window.addEventListener("keydown", (e) => {
    console.log(e.key)
    if (e.key == "Escape") {
      closeSpace();
    }
  })

  dateInput.setAttribute('aria-label', 'Select date for lunar snapshot');
  const today = new Date().toISOString().slice(0, 10);
  dateInput.value = today;
  displayDate.textContent = today;
  // const data = await fetchForDate(today);
  // canvasDraw(data);
})();
