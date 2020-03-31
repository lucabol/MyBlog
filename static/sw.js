// the cache version gets updated every time there is a new deployment
const CACHE_VERSION = 11;
const CURRENT_CACHE = `v${CACHE_VERSION}`;

// these are the routes we are going to cache for offline support
const cacheFiles = ['/', '/index.html', '/offline/', '/offline/index.html'];

// these are the file type to cache with stale while revalidate
const staleTypes = ['.woff', 'woff2', 'ttf']

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
self.addEventListener('fetch', event => {
  if(event.request.method === 'GET' ) 
    if(staleTypes.some(v => event.request.url.includes(v))) {
      // For fonts returns it from cache and asynchronously download the latest one in case it changed
      event.respondWith(caches.open(CURRENT_CACHE).then(cache => cache.match(event.request).then(response => {
        const fetchPromise = fetch(event.request).then(networkResponse => {
          if(networkResponse.status < 400 && event.request.url.indexOf('http') === 0) cache.put(event.request, networkResponse.clone())
          return networkResponse
        })
        return response || fetchPromise
      })))
    } else {
      // For all the rest return it from the network, cache it and, if network error from cache
      event.respondWith(fetch(event.request).then(networkResponse => {
        const clonedResponse = networkResponse.clone()
        caches.open(CURRENT_CACHE).then(cache => {
          if(!(event.request.url.indexOf('http') === 0)){
            return;
          }
          cache.put(event.request, clonedResponse)
        })
        return networkResponse;
      }).catch(e => caches.open(CURRENT_CACHE).then(cache => cache.match(event.request))))
    }
})