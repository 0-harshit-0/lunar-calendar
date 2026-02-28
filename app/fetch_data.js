const API_BASE = 'http://127.0.0.1:8000'; //'https://lunar-calendar-laeb.onrender.com';

async function fetchForDate(isoDate) {
  setStatus('Loading data...');
  fetchBtn.disabled = true;

  try {
    // 1. check localStorage cache
    const cached = getCachedDate('lunarCache', isoDate);
    if (cached) {
      // move the rendering part out and keep it only fetch
      renderData(cached.data);
      setStatus('Loaded from cache');
      enableJsonActions(cached.data);
      return cached.data;
    }

    // 2. fetch from API
    const url = new URL(API_BASE+"/info");
    url.searchParams.set('timestamp', isoDate);

    const res = await fetch(url.toString(), { cache: 'no-store' });
    if (!res.ok) throw new Error('Network error ' + res.status);

    const data = await res.json();

    // 3. store in cache
    setCachedDate('lunarCache', isoDate, data);

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

async function fetchPlanetsForDate(isoDate) {
  setStatus('Loading planets...');

  try {
    // 1. check cache
    const cached = getCachedDate('planets', isoDate);
    if (cached) {
      setStatus('Planets loaded from cache');
      return cached.data;
    }

    // 2. fetch from API
    const url = new URL(API_BASE + '/planets');
    url.searchParams.set('timestamp', isoDate);

    const res = await fetch(url.toString(), { cache: 'no-store' });
    if (!res.ok) throw new Error('Network error ' + res.status);

    const data = await res.json();

    // 3. store in cache
    setCachedDate('planets', isoDate, data);

    setStatus('Planets loaded');
    return data;
  } catch (err) {
    console.error(err);
    setStatus('Could not fetch planets: ' + err.message, true);
    return null;
  }
}
