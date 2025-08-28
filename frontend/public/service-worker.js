const CACHE_NAME = 'app-cache-v1';
const urlsToCache = [
  '/static/js/main.js',
  '/static/css/main.css',
  // andere assets
];

// Install event: cache alle statische assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch event: network-first voor index.html, cache-first voor andere assets
self.addEventListener('fetch', event => {
  const { request } = event;

  if (request.mode === 'navigate') {
    // Network-first voor HTML pagina’s (zoals index.html)
    event.respondWith(
      fetch(request)
        .then(response => {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(request, response.clone());
            return response;
          });
        })
        .catch(() => caches.match(request)) // fallback naar cache
    );
  } else {
    // Cache-first voor andere requests (CSS/JS/images)
    event.respondWith(
      caches.match(request).then(response => {
        return response || fetch(request).then(resp => {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(request, resp.clone());
            return resp;
          });
        });
      })
    );
  }
});

// Activate event: oude caches opruimen
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) return caches.delete(name);
        })
      )
    )
  );
});
