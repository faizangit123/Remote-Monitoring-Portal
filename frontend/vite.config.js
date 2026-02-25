// vite.config.js
// Vite is our build tool — this configures how it works

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // react() plugin enables JSX transformation and React Fast Refresh
  // (Fast Refresh = code changes show instantly without full page reload)

  server: {
    port: 5173,
    // Run dev server on port 5173 (default for Vite)

    proxy: {
      // Proxy API requests to backend during development
      // This avoids CORS issues when running frontend and backend separately
      
      '/api': {
        target: 'http://localhost:8000',
        // All requests to /api/... get sent to http://localhost:8000/api/...
        changeOrigin: true,
      },
      
      '/ws': {
        target: 'ws://localhost:8000',
        // All WebSocket connections to /ws/... go to backend
        ws: true,
        // ws: true tells Vite this is a WebSocket proxy
        changeOrigin: true,
      },
    },
  },
})