import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Ensure it binds to all interfaces, critical for Codespaces/Docker
    port: 5173,
    // Add allowedHosts to prevent the "Invalid Host header" issue in Codespaces
    allowedHosts: 'all'
  }
})
