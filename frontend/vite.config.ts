import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  // Keep the original frontend structure intact while allowing the root
  // package.json to orchestrate both frontend and backend with one command.
  root: frontendRoot,
  plugins: [react()],
  css: {
    // Explicitly configure PostCSS here. This prevents Tailwind from being
    // skipped when Vite is launched from the project root via npm run dev.
    postcss: {
      plugins: [
        tailwindcss({ config: path.join(frontendRoot, 'tailwind.config.js') }),
        autoprefixer(),
      ],
    },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
