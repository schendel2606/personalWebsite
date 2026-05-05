// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://niv.schendel.me',
  integrations: [react()],
  build: {
    format: 'directory',  // /projects/ instead of /projects.html for cleaner URLs
  },
  vite: {
    server: {
      // Allow loading content from monorepo root
      fs: { allow: ['..', '../..'] },
    },
  },
});