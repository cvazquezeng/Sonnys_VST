const cacheName = 'your-app-cache-v1';
const assetsToCache = [
  '/',
  '/static/css/custom.css',
  '/static/css/dashboard.css',
  '/static/css/dashboard2.css',
  '/static/css/delete_stack.css',
  '/static/css/general.css',
  '/static/css/home_status.css',
  '/static/css/login.css',
  '/static/css/navbar.css',
  '/static/css/old_style.css',
  '/static/css/open_tickets.css',
  '/static/images/android-chrome-192x192.png',
  '/static/images/android-chrome-512x512.png',
  '/static/images/apple-touch-icon.png',
  '/static/images/favicon-16x16.png',
  '/static/images/favicon-32x32.png',
  '/static/images/favicon.ico',
  '/static/js/collapse.js',
  '/static/js/dashboard.js',
  '/static/js/dashboard2.js',
  '/static/js/home_status.js',
  '/static/js/inactivity-logout.js',
  '/static/js/navbar-buttons.js',
  '/static/js/open_tickets.js',
  '/static/js/script.js',
  '/static/js/stack_control_5605.js',
  '/static/js/stack_control_5607.js',
  '/static/js/stack_status_5605.js',
  '/static/js/stack_status_5607.js',
  '/static/js/tableini.js',
  '/static/manifest.json'
];

// Install event: caching resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(cacheName).then(cache => {
      return cache.addAll(assetsToCache);
    })
  );
});

// Fetch event: serving cached resources when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

self.addEventListener('push', event => {
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/images/favicon-32x32.png',
    badge: '/static/images/favicon-32x32.png',
    data: {
      url: data.url
    }
  };
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
// Activate event: cleaning up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [cacheName];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
