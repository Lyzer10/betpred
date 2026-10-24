// Push notifications, loaded into the generated service worker (vite.config.ts workbox.importScripts).
self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  event.waitUntil(self.registration.showNotification(data.title || "BetPredz", {
    body: data.body || "",
    icon: "/icons/icon-192.png",
    badge: "/icons/favicon.png",
    tag: data.tag || "betpredz",
    data: { url: data.url || "/" },
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
    const open = clients.find((client) => "focus" in client);
    return open ? open.focus() : self.clients.openWindow(url);
  }));
});
