import { openSpace, closeSpace, init as spaceInit } from "./space_canvas.js";

// initial load
(async function () {
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
    let datetime = dateInput.value;
    if (!datetime) {
      setStatus('Please choose a date', true);
      return;
    }
    // datetime-local drops seconds. Append :00 for the Python backend
    if (datetime.length === 16) datetime += ":00";

    const localDate = new Date(datetime);
    const utcString = localDate.toISOString().replace(".000Z", "");

    const data = await fetchForDate(utcString);
    canvasDraw(data);
  });

  calendarCanvas.addEventListener('dblclick', async (e) => {
    let datetime = dateInput.value;
    if (!datetime) {
      setStatus('Please choose a date', true);
      return;
    }
    // datetime-local drops seconds. Append :00 for the Python backend
    if (datetime.length === 16) datetime += ":00";

    const localDate = new Date(datetime);
    const utcString = localDate.toISOString().replace(".000Z", "");

    const data = await fetchForDate(utcString);
    
    openSpace();
    spaceInit(data);
  });

  window.addEventListener("keydown", (e) => {
    if (e.key == "Escape") {
      closeSpace();
    }
  })

  dateInput.setAttribute('aria-label', 'Select date for lunar snapshot');

  // Get current local time formatted for <input type="datetime-local">
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  const todayLocal = now.toISOString().slice(0, 16); // YYYY-MM-DDTHH:MM
  
  dateInput.value = todayLocal;
  dateForm.submit();
})();
