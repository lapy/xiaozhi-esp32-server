/* global self, workbox */

// Custom Service Worker installation and activation handling logic
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// CDN resource list
const CDN_CSS = [
  'https://unpkg.com/element-ui@2.15.14/lib/theme-chalk/index.css',
  'https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css'
];

const CDN_JS = [
  'https://unpkg.com/vue@2.6.14/dist/vue.min.js',
  'https://unpkg.com/vue-router@3.6.5/dist/vue-router.min.js',
  'https://unpkg.com/vuex@3.6.2/dist/vuex.min.js',
  'https://unpkg.com/element-ui@2.15.14/lib/index.js',
  'https://unpkg.com/axios@0.27.2/dist/axios.min.js',
  'https://unpkg.com/opus-decoder@0.7.7/dist/opus-decoder.min.js'
];

// Automatically executed when Service Worker is injected into manifest
const manifest = self.__WB_MANIFEST || [];

// Check if CDN mode is enabled
const isCDNEnabled = manifest.some(entry => 
  entry.url === 'cdn-mode' && entry.revision === 'enabled'
);

console.log(`Service Worker initialized, CDN mode: ${isCDNEnabled ? 'enabled' : 'disabled'}`);

// Inject workbox related code
importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');
workbox.setConfig({ debug: false });

// Enable workbox
workbox.core.skipWaiting();
workbox.core.clientsClaim();

// Pre-cache offline page
const OFFLINE_URL = '/offline.html';
workbox.precaching.precacheAndRoute([
  { url: OFFLINE_URL, revision: null }
]);

// Add install completion event handler, display install message in console
self.addEventListener('install', event => {
  if (isCDNEnabled) {
    console.log('Service Worker installed, starting to cache CDN resources');
  } else {
    console.log('Service Worker installed, CDN mode disabled, only cache local resources');
  }
  
  // Ensure offline page is cached
  event.waitUntil(
    caches.open('offline-cache').then((cache) => {
      return cache.add(OFFLINE_URL);
    })
  );
});

// Add activation event handler
self.addEventListener('activate', event => {
  console.log('Service Worker activated, now controlling the page');
  
  // Clean up old version cache
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          // Clean up cache except current version
          return cacheName.startsWith('workbox-') && !workbox.core.cacheNames.runtime.includes(cacheName);
        }).map(cacheName => {
          return caches.delete(cacheName);
        })
      );
    })
  );
});

// Add fetch event interceptor to check if CDN resources hit cache
self.addEventListener('fetch', event => {
  // Only monitor CDN resource caching when CDN mode is enabled
  if (isCDNEnabled) {
    const url = new URL(event.request.url);
    
    // For CDN resources, output cache hit information
    if ([...CDN_CSS, ...CDN_JS].includes(url.href)) {
      // Do not interfere with normal fetch process, only add logs
      console.log(`Request CDN resource: ${url.href}`);
    }
  }
});

// Only cache CDN resources in CDN mode
if (isCDNEnabled) {
  // Cache CDN CSS resources
  workbox.routing.registerRoute(
    ({ url }) => CDN_CSS.includes(url.href),
    new workbox.strategies.CacheFirst({
      cacheName: 'cdn-stylesheets',
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxAgeSeconds: 365 * 24 * 60 * 60, // Increase to 1 year cache
          maxEntries: 10, // Maximum 10 CSS files cached
        }),
        new workbox.cacheableResponse.CacheableResponsePlugin({
          statuses: [0, 200], // Cache successful responses
        }),
      ],
    })
  );

  // Cache CDN JS resources
  workbox.routing.registerRoute(
    ({ url }) => CDN_JS.includes(url.href),
    new workbox.strategies.CacheFirst({
      cacheName: 'cdn-scripts',
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxAgeSeconds: 365 * 24 * 60 * 60, // Increase to 1 year cache
          maxEntries: 20, // Maximum 20 JS files cached
        }),
        new workbox.cacheableResponse.CacheableResponsePlugin({
          statuses: [0, 200], // Cache successful responses
        }),
      ],
    })
  );
}

// Whether CDN mode is enabled or not, cache local static resources
workbox.routing.registerRoute(
  /\.(?:js|css|png|jpg|jpeg|svg|gif|ico|woff|woff2|eot|ttf|otf)$/,
  new workbox.strategies.StaleWhileRevalidate({
    cacheName: 'static-resources',
    plugins: [
      new workbox.expiration.ExpirationPlugin({
        maxAgeSeconds: 7 * 24 * 60 * 60, // 7 days cache
        maxEntries: 50, // Maximum 50 files cached
      }),
    ],
  })
);

// Cache HTML pages
workbox.routing.registerRoute(
  /\.html$/,
  new workbox.strategies.NetworkFirst({
    cacheName: 'html-cache',
    plugins: [
      new workbox.expiration.ExpirationPlugin({
        maxAgeSeconds: 1 * 24 * 60 * 60, // 1 day cache
        maxEntries: 10, // Maximum 10 HTML files cached
      }),
    ],
  })
);

// Offline page - use more reliable handling
workbox.routing.setCatchHandler(async ({ event }) => {
  // Return appropriate default page based on request type
  switch (event.request.destination) {
    case 'document':
      // If it is a web page request, return offline page
      return caches.match(OFFLINE_URL);
    default:
      // All other requests return error
      return Response.error();
  }
}); 