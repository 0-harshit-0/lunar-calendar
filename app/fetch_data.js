const API_BASE = 'https://lunar-calendar-laeb.onrender.com/info';

async function fetchForDate(isoDate) {
  setStatus('Loading data...');
  fetchBtn.disabled = true;

  try {
    // 1. check localStorage cache
    const cached = getCachedDate(isoDate);
    if (cached) {
      // move the rendering part out and keep it only fetch
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

async function fetchPlanets() {
  try {
    console.log(2)
  } catch (err) {
    console.error(err);
    return null;
  } finally {
  }
}