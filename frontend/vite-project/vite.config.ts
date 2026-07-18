import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The Laravel backend runs at 127.0.0.1:8000. We proxy the API endpoints
// (and the /storage path used for product images) so the browser treats
// everything as same-origin — this keeps the session cookie working.
const backend = 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Only /api and /storage are proxied to Laravel. All other paths are
      // served by Vite (React Router handles /login, /register, / client-side).
      '/api': backend,
      '/storage': backend,
    },
  },
});
