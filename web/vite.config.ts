import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["icons/favicon.png", "icons/apple-touch-icon.png"],
      manifest: {
        name: "BetPredz",
        short_name: "BetPredz",
        description: "Premier League probabilities, accumulator slips and value checks",
        theme_color: "#000e2d",
        background_color: "#000e2d",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "icons/icon-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // Predictions change daily: always try the network first, fall back offline.
        runtimeCaching: [{
          urlPattern: /\/data\/predictions\.json$/,
          handler: "NetworkFirst",
          options: { cacheName: "predictions" },
        }],
      },
    }),
  ],
});
