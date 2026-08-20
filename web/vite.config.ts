import { defineConfig, type ProxyOptions } from 'vite'
import react from '@vitejs/plugin-react'

/** Proxy API paths, but let the SPA handle full-page HTML navigations. */
function apiProxy(pathFilter: string): [string, ProxyOptions] {
  return [
    pathFilter,
    {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      bypass(req) {
        const accept = req.headers.accept ?? ''
        if (accept.includes('text/html')) {
          return '/index.html'
        }
      },
    },
  ]
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries([
      apiProxy('/auth'),
      apiProxy('/shops'),
      apiProxy('/heatmap'),
      apiProxy('/analytics'),
      apiProxy('/stream'),
      apiProxy('/admin'),
      apiProxy('/health'),
    ]),
  },
})
