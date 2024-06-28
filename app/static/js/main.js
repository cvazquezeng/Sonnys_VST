if ('serviceWorker' in navigator && 'PushManager' in window) {
  navigator.serviceWorker.register('/static/service-worker.js')
    .then(registration => {
      console.log('Service Worker registered with scope:', registration.scope);
      return registration;
    })
    .then(registration => {
      // Request notification permission
      Notification.requestPermission(permission => {
        if (permission === 'granted') {
          console.log('Notification permission granted.');
          subscribeUserToPush(registration);
        } else {
          console.log('Notification permission denied.');
        }
      });
    })
    .catch(error => {
      console.error('Service Worker registration failed:', error);
    });
} else {
  console.warn('Push messaging is not supported');
}

function subscribeUserToPush(registration) {
  const vapidPublicKey = 'BOvF7YOswNRSP8QytJ0d_AbKp9vOnMwopNHfLhsrj-IXbp95vOajtzPeBN3L1oqbAdUUloUKxiyGS3xw_d3NWbs';
  const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);
  registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: convertedVapidKey
  })
  .then(subscription => {
    console.log('User is subscribed:', subscription);
    // Send subscription to the server
    fetch('/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(subscription)
    });
  })
  .catch(error => {
    if (Notification.permission === 'denied') {
      console.warn('Permission for notifications was denied');
    } else {
      console.error('Failed to subscribe the user: ', error);
    }
  });
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
