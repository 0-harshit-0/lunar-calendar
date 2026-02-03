const LS_KEY = 'lunarCache';
const MAX_CACHE_DAYS = 10;
function loadCache() {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY)) || {};
  } catch {
    return {};
  }
}

function saveCache(cache) {
  localStorage.setItem(LS_KEY, JSON.stringify(cache));
}

function getCachedDate(date) {
  const cache = loadCache();
  return cache[date] || null;
}

function setCachedDate(date, data) {
  const cache = loadCache();

  // insert or update
  cache[date] = {
    data,
    storedAt: Date.now()
  };

  // enforce max 10 days
  const entries = Object.entries(cache)
    .sort((a, b) => a[1].storedAt - b[1].storedAt);

  while (entries.length > MAX_CACHE_DAYS) {
    const [oldestKey] = entries.shift();
    delete cache[oldestKey];
  }

  saveCache(cache);
}

// API endpoint
const API_BASE = 'https://lunar-calendar-laeb.onrender.com/info';

// Elements
const dateInput = document.getElementById('dateInput');
const dateForm = document.getElementById('dateForm');
const displayDate = document.getElementById('displayDate');
const statusEl = document.getElementById('status');
const fetchBtn = document.getElementById('fetchBtn');
const downloadJsonBtn = document.getElementById('downloadJson');
const copyJsonBtn = document.getElementById('copyJson');

const ayanaEl = document.getElementById('ayana');
const rituEl = document.getElementById('ritu');
const masaEl = document.getElementById('masa');
const pakshaEl = document.getElementById('paksha');
const tithiEl = document.getElementById('tithi');
const phaseEl = document.getElementById('phase');
const fastingEl = document.getElementById('fasting');
const sunRashiEl = document.getElementById('sunRashi');
const moonRashiEl = document.getElementById('moonRashi');
const sunLonEl = document.getElementById('sunLon');
const moonLonEl = document.getElementById('moonLon');
const longAngleEl = document.getElementById('longAngle');
const sunXYZPre = document.getElementById('sunXYZ');
const moonXYZPre = document.getElementById('moonXYZ');


function formatNumber(n, digits = 6) {
  if (typeof n !== 'number' || !isFinite(n)) return 'N/A';
  return Number(n).toFixed(digits);
}

function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.classList.toggle('text-red-600', isError);
  statusEl.classList.toggle('text-slate-500', !isError);
}

async function fetchForDate(isoDate) {
  setStatus('Loading data...');
  fetchBtn.disabled = true;

  try {
    // 1. check localStorage cache
    const cached = getCachedDate(isoDate);
    if (cached) {
      renderData(cached.data);
      setStatus('Loaded from cache');
      enableJsonActions(cached.data);
      return cached.data;
    }

    // 2. fetch from API
    const url = new URL(API_BASE);
    url.searchParams.set('date', isoDate);

    const res = await fetch(url.toString(), { cache: 'no-store' });
    if (!res.ok) throw new Error('Network error ' + res.status);

    const data = await res.json();

    // 3. store in cache
    setCachedDate(isoDate, data);

    renderData(data);
    setStatus('Data loaded');
    enableJsonActions(data);

    return data;
  } catch (err) {
    console.error(err);
    setStatus('Could not fetch data: ' + err.message, true);
    clearDisplay();
    disableJsonActions();
    return null;
  } finally {
    fetchBtn.disabled = false;
  }
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
  fastingEl.textContent = (data.fasting_days && data.fasting_days.length) ? data.fasting_days.map(z => z.name).join(", ") : 'N/A';

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
      { "name": "tithi", "value": data.tithi }
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
  const els = [ayanaEl, rituEl, masaEl, pakshaEl, tithiEl, phaseEl, fastingEl, sunRashiEl, moonRashiEl, sunLonEl, moonLonEl, longAngleEl];
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

function canvasDraw(data) {
  if (!data) return;
  
  const dpr = window.devicePixelRatio || 1;

  console.log(data)
  const sunLongitudeDeg = data.surya_longitude_deg;
  const moonLongitudeDeg = data.chandra_longitude_deg;

  const canvas = document.getElementById('skyCanvas');
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();

  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  // Visual scale (purely illustrative)
  const sunRadius = 90;
  const moonRadius = 65;

  // Convert degrees to canvas angle
  // Canvas: 0 rad = right, positive clockwise
  // Astronomy: 0° = Aries direction, counter-clockwise
  function toCanvasAngle(deg) {
    return (deg - 90) * Math.PI / 180;
  }

  function polarToXY(radius, angle) {
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle)
    };
  }

  // Clear
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw reference circle (ecliptic)
  ctx.beginPath();
  ctx.arc(cx, cy, sunRadius, 0, Math.PI * 2);
  ctx.strokeStyle = '#e5e7eb';
  ctx.stroke();

    // Degree markers around the ecliptic
  const labelRadius = sunRadius + 18;
  const tickInner = sunRadius - 4;
  const tickOuter = sunRadius + 4;

  ctx.font = `${10 * dpr}px system-ui, sans-serif`;
  ctx.fillStyle = '#475569';
  ctx.strokeStyle = '#94a3b8';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  for (let deg = 0; deg < 360; deg += 10) {
    const angle = toCanvasAngle(deg);

    const inner = polarToXY(tickInner, angle);
    const outer = polarToXY(tickOuter, angle);

    // Tick mark
    ctx.beginPath();
    ctx.moveTo(inner.x, inner.y);
    ctx.lineTo(outer.x, outer.y);
    ctx.stroke();

    // Label every 30°
    if (deg % 30 === 0) {
      const labelPos = polarToXY(labelRadius, angle);
      ctx.fillText(`${deg}°`, labelPos.x, labelPos.y);
    }
  }

  // Earth
  ctx.beginPath();
  ctx.arc(cx, cy, 8, 0, Math.PI * 2);
  ctx.fillStyle = '#22c55e';
  ctx.fill();

  // Sun
  const sunAngle = toCanvasAngle(sunLongitudeDeg);
  const sunPos = polarToXY(sunRadius, sunAngle);

  ctx.beginPath();
  ctx.arc(sunPos.x, sunPos.y, 10, 0, Math.PI * 2);
  ctx.fillStyle = '#facc15';
  ctx.fill();

  // Moon
  const moonAngle = toCanvasAngle(moonLongitudeDeg);
  const moonPos = polarToXY(moonRadius, moonAngle);

  ctx.beginPath();
  ctx.arc(moonPos.x, moonPos.y, 6, 0, Math.PI * 2);
  ctx.fillStyle = '#9ca3af';
  ctx.fill();

  // Lines from Earth
  ctx.strokeStyle = '#111827';
  ctx.lineWidth = 1;

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(sunPos.x, sunPos.y);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(moonPos.x, moonPos.y);
  ctx.stroke();

  // Aries direction marker (0°)
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + sunRadius, cy);
  ctx.setLineDash([4, 4]);
  ctx.strokeStyle = '#94a3b8';
  ctx.stroke();
  ctx.setLineDash([]);
}

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

// initial load
(async function init() {
  dateInput.setAttribute('aria-label', 'Select date for lunar snapshot');
  const today = new Date().toISOString().slice(0, 10);
  dateInput.value = today;
  displayDate.textContent = today;
  const data = await fetchForDate(today);
  canvasDraw(data);
})();
