// the cache version gets updated every time there is a new deployment
const CACHE_VERSION = 11;
const CURRENT_CACHE = `v${CACHE_VERSION}`;

// these are the routes we are going to cache for offline support
const cacheFiles = ['/', '/index.html', '/offline/', '/offline/index.html'];

// these are the file type to cache with stale while revalidate
const staleTypes = [/^font\//i]

// on activation we clean up the previously registered service workers
self.addEventListener('activate', evt =>
  evt.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CURRENT_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  )
);

// on install we download the routes we want to cache for offline
self.addEventListener('install', evt =>
  evt.waitUntil(
    caches.open(CURRENT_CACHE).then(cache => {
      return cache.addAll(cacheFiles);
    })
  )
);

// https://developers.google.com/web/fundamentals/instant-and-offline/offline-cookbook#stale-while-revalidate
self.addEventListener('fetch', function(event) {
  if(event.request.method === "GET") {
    event.respondWith(
      caches.open(CURRENT_CACHE).then(function(cache) {
        return cache.match(event.request).then(function(response) {
          var fetchPromise = fetch(event.request).then(function(networkResponse) {
            console.log(`cached: ${networkResponse.headers.get('content-type')}`)
            // Just add to the cache the stale types
            if(networkResponse.status < 400 && networkResponse.headers.has('content-type') && networkResponse.headers.get('content-type').match(staleTypes)) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          return response || fetchPromise;
        })
        .catch(function(networkResponse) {
            console.log(`network: ${networkResponse.headers.get('content-type')}`)
          return fetch(event.request).then(function(networkResponse) {
            // Just add to the cache the stale types
            if(networkResponse.status < 400 && networkResponse.headers.has('content-type') && networkResponse.headers.get('content-type').match(staleTypes)) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })

        })
      })
    );
  }
});

