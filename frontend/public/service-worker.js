const CACHE_NAME = 'app-cache-v1';

const urlsToCache = [
  '/static/js/main.js',
  '/static/css/main.css',
  '/favicon.ico',
  '/manifest.json'
];

// Install event: cache alle statische assets veilig
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.all(
        urlsToCache.map(url =>
          fetch(url)
            .then(response => {
              if (!response.ok) throw new Error(`Request failed: ${url}`);
              return cache.put(url, response);
            })
            .catch(err => console.warn('Cache failed for', url, err))
        )
      );
    }).then(() => self.skipWaiting())
  );
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
    ).then(() => self.clients.claim())
  );
});

// Fetch event: network-first voor HTML, cache-first voor andere assets
self.addEventListener('fetch', event => {
  const { request } = event;

  if (request.mode === 'navigate') {
    // Network-first voor pagina's
    event.respondWith(
      fetch(request)
        .then(response => {
          // Update cache met nieuwste index.html
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(request, response.clone());
            return response;
          });
        })
        .catch(() => caches.match(request)) // fallback naar cache
    );
  } else {
    // Cache-first voor andere requests (JS/CSS/images)
    event.respondWith(
      caches.match(request).then(response => {
        return response || fetch(request).then(resp => {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(request, resp.clone());
            return resp;
          });
        }).catch(err => {
          console.warn('Fetch failed for', request.url, err);
        });
      })
    );
  }
});
