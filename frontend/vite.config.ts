/// <reference types="vitest/config" />
import basicSsl from '@vitejs/plugin-basic-ssl'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const BACKEND_URL = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // The session cookie is Secure by design (BUSINESS_RULES/decisão de
    // auth) and a real browser silently drops a Secure cookie over plain
    // http://. Rather than weakening that in code, the dev server itself
    // runs over HTTPS (self-signed — the browser will ask you to accept it
    // once). The backend stays plain HTTP; only Vite's proxy talks to it
    // server-side, so this doesn't need to reach the browser over TLS.
    basicSsl(),
  ],
  server: {
    // Proxies API calls through the Vite dev server so the browser only ever
    // talks to one origin — avoids cross-origin cookie issues with the
    // Secure/SameSite=Lax session cookie during local development.
    proxy: {
      '/auth': BACKEND_URL,
      '/tasks': BACKEND_URL,
      '/events': BACKEND_URL,
      '/goals': BACKEND_URL,
      '/market': BACKEND_URL,
      '/finance': BACKEND_URL,
      // A resposta do LLM local pode levar bem mais que o padrão do proxy
      // (benchmark real: ~1-20s conforme o pedido) — timeout maior só aqui.
      '/conversation': { target: BACKEND_URL, timeout: 65000, proxyTimeout: 65000 },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
    globals: true,
  },
})
