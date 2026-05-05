import { getViteConfig } from 'astro/config';

export default getViteConfig({
  test: {
    globals: false,
  },
});
