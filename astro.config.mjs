import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import { rehypeR2Images } from './src/lib/markdown-r2-images.mjs';

export default defineConfig({
  site: 'https://kieferwaight.com',
  integrations: [
    sitemap({
      namespaces: { news: false, xhtml: false, image: false, video: false },
    }),
  ],
  markdown: {
    processor: unified({ rehypePlugins: [rehypeR2Images] }),
    shikiConfig: { theme: 'github-dark-default' },
    syntaxHighlight: 'shiki',
  },
});
