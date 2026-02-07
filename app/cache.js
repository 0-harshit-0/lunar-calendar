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