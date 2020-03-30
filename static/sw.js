// the cache version gets updated every time there is a new deployment
const CACHE_VERSION = 10;
const CURRENT_CACHE = `v${CACHE_VERSION}`;

// these are the routes we are going to cache for offline support
const cacheFiles = ['/', '/index.html', '/offline/', '/offline/index.html'];

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

self.addEventListener('fetch', evt =>
    evt.respondWith(tryFetch(evt.request)))

const tryFetch = request =>
    fetch(request)
        .then(toCacheAndReturn(request))
        .catch(fromCacheOrOffline(request))

const toCacheAndReturn = request => response =>
    caches
        .open(CURRENT_CACHE)
        .then(cache => {
            if(request.method === 'GET')
                cache.put(request, response.clone())
            return response
        })

const fromCacheOrOffline = request => err =>
    caches
        .open(CURRENT_CACHE)
        .then(cache => 
            cache.match(request)
                 .then(response => response || cache.match("/offline/"))
                 .catch(error => cache.match("/offline/"))
        )

