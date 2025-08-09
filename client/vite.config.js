import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@root': path.resolve(__dirname, '..'),
      '@stylesRoot': path.resolve(__dirname, '../styles')
    }
  },
  server: {
    port: 5173,
    open: false,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY || 'http://localhost:3000',
        changeOrigin: true
      }
    },
    fs: {
      allow: [path.resolve(__dirname, '..')] // allow importing from project root
    }
  }
})
