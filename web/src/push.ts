/** Phone notifications from the app itself (Web Push). The public key pairs with the
 * VAPID_PRIVATE_KEY repository secret that scripts/notify.py signs with. */
export const VAPID_PUBLIC_KEY = "BNSQvQ7J5UHDI4fJ4qoVF4t33xzF-TmsUPE0k-zXYvBsoXp531wXjb1uj9fxSm0_uFQUEbKm2xaQNCIoC-cV_iI";

export const pushSupported = () =>
  typeof window !== "undefined" && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;

function keyBytes(base64url: string) {
  const padded = (base64url + "=".repeat((4 - (base64url.length % 4)) % 4)).replace(/-/g, "+").replace(/_/g, "/");
  return Uint8Array.from(atob(padded), (c) => c.charCodeAt(0));
}

/** Ask permission and subscribe this phone; returns the code the workflow needs, or an error message. */
export async function enablePush(): Promise<{ code?: string; error?: string }> {
  if (!pushSupported()) return { error: "This browser cannot show notifications. On iPhone, add BetPredz to the Home Screen first." };
  const permission = await Notification.requestPermission();
  if (permission !== "granted") return { error: "Notifications were not allowed. You can allow them in the browser's site settings." };
  const registration = await navigator.serviceWorker.ready;
  const subscription = await registration.pushManager.getSubscription()
    ?? await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyBytes(VAPID_PUBLIC_KEY) });
  return { code: JSON.stringify(subscription.toJSON()) };
}

/** The subscription code if this phone is already subscribed. */
export async function currentPushCode(): Promise<string | null> {
  if (!pushSupported() || Notification.permission !== "granted") return null;
  const subscription = await (await navigator.serviceWorker.ready).pushManager.getSubscription();
  return subscription ? JSON.stringify(subscription.toJSON()) : null;
}
