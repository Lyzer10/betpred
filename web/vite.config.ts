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
      includeAssets: ["icons/icon.svg"],
      manifest: {
        name: "PL Predictor",
        short_name: "PL Predictor",
        description: "Premier League probabilities, accumulator slips and value checks",
        theme_color: "#0f1a2e",
        background_color: "#0f1a2e",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
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
