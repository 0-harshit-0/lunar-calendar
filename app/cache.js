const MAX_CACHE_DAYS = 3;

function loadCache(key) {
  try {
    return JSON.parse(localStorage.getItem(key)) || {};
  } catch {
    return {};
  }
}

function saveCache(key, cache) {
  localStorage.setItem(key, JSON.stringify(cache));
}

function getCachedDate(key, date) {
  const cache = loadCache(key);
  return cache[date] || null;
}

function setCachedDate(key, date, data) {
  const cache = loadCache(key);

  // insert or update
  cache[date] = {
    data,
    storedAt: Date.now()
  };

  // enforce max days
  const entries = Object.entries(cache)
    .sort((a, b) => a[1].storedAt - b[1].storedAt);

  while (entries.length > MAX_CACHE_DAYS) {
    const [oldestKey] = entries.shift();
    delete cache[oldestKey];
  }

  saveCache(key, cache);
}