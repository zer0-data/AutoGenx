// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/AutoGenx/",
  server: {
    proxy: {
      "/api": "http://localhost:5500"
    }
  }
})

