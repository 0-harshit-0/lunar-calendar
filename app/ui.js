function formatNumber(n, digits = 6) {
  if (typeof n !== 'number' || !isFinite(n)) return 'N/A';
  return Number(n).toFixed(digits);
}

function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.classList.toggle('text-red-600', isError);
  statusEl.classList.toggle('text-slate-500', !isError);
}

function renderData(data) {
  const iso = data.date || dateInput.value || exampleDate;
  displayDate.textContent = iso;

  // plain text fields
  ayanaEl.textContent = data.ayana ?? 'N/A';
  rituEl.textContent = data.ritu ?? 'N/A';
  masaEl.textContent = data.masa ?? 'N/A';
  pakshaEl.textContent = data.paksha ?? 'N/A';
  tithiEl.textContent = data.tithi ?? 'N/A';
  phaseEl.textContent = data.phase ?? 'N/A';
  upavaasEl.textContent = (data.upavaas && data.upavaas.length) ? data.upavaas.map(z => z.name).join(", ") : 'N/A';
  grahanaEl.textContent = (data.grahana && data.grahana !== "None") 
  ? (data.grahana === "Surya" ? "Solar Eclipse" : "Lunar Eclipse")
  : "None";

  sunRashiEl.textContent = data.surya_rashi ?? 'N/A';
  moonRashiEl.textContent = data.chandra_rashi ?? 'N/A';
  sunLonEl.textContent = (typeof data.surya_longitude_deg === 'number') ? formatNumber(data.surya_longitude_deg, 6) + '°' : 'N/A';
  moonLonEl.textContent = (typeof data.chandra_longitude_deg === 'number') ? formatNumber(data.chandra_longitude_deg, 6) + '°' : 'N/A';
  longAngleEl.textContent = (typeof data.longitudinal_angle_deg === 'number') ? formatNumber(data.longitudinal_angle_deg, 6) + '°' : 'N/A';

  sunXYZPre.textContent = Array.isArray(data.surya_xyz) ? '[' + data.surya_xyz.map(n => formatNumber(n, 3)).join(', ') + ']' : 'N/A';
  moonXYZPre.textContent = Array.isArray(data.chandra_xyz) ? '[' + data.chandra_xyz.map(n => formatNumber(n, 3)).join(', ') + ']' : 'N/A';

  updateJsonLdTag(data);
}

function updateJsonLdTag(data) {
  let existing = document.querySelector('script[type="application/ld+json"][data-generated="lunar-info"]');
  const payload = {
    "@context": "https://schema.org",
    "@type": "Observation",
    "name": "Lunar snapshot for " + (data.date || ''),
    "observationDate": data.date || '',
    "additionalProperty": [
      { "name": "ayana", "value": data.ayana },
      { "name": "ritu", "value": data.ritu },
      { "name": "masa", "value": data.masa },
      { "name": "paksha", "value": data.paksha },
      { "name": "tithi", "value": data.tithi },
      { "name": "grahana", "value": data.grahana }
    ]
  };
  if (existing) existing.textContent = JSON.stringify(payload);
  else {
    const s = document.createElement('script');
    s.type = 'application/ld+json';
    s.setAttribute('data-generated', 'lunar-info');
    s.textContent = JSON.stringify(payload);
    document.head.appendChild(s);
  }
}

function clearDisplay() {
  displayDate.textContent = exampleDate;
  const els = [ayanaEl, rituEl, masaEl, pakshaEl, tithiEl, phaseEl, upavaasEl, sunRashiEl, moonRashiEl, sunLonEl, moonLonEl, longAngleEl, grahanaEl];
  els.forEach(e => e.textContent = 'N/A');
  sunXYZPre.textContent = moonXYZPre.textContent = 'N/A';
}

function enableJsonActions(data) {
  downloadJsonBtn.disabled = false;
  copyJsonBtn.disabled = false;

  downloadJsonBtn.onclick = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lunar-${data.date || 'data'}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  copyJsonBtn.onclick = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setStatus('JSON copied to clipboard');
    } catch (err) {
      setStatus('Could not copy JSON: ' + err.message, true);
    }
  };
}

function disableJsonActions() {
  downloadJsonBtn.disabled = true;
  copyJsonBtn.disabled = true;
  downloadJsonBtn.onclick = null;
  copyJsonBtn.onclick = null;
}

