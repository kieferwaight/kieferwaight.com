import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://kieferwaight.com',
  integrations: [sitemap()],
  image: {
    layout: 'constrained',
    remotePatterns: [{ protocol: 'https', hostname: 'images.kieferwaight.com' }],
  },
  markdown: {
    shikiConfig: { theme: 'github-dark-default' },
    syntaxHighlight: 'shiki',
  },
});
