/// <reference types="vitest/config" />
import { getViteConfig } from 'astro/config';

export default getViteConfig({
  test: {
    include: ['tests/**/*.test.{js,mjs,ts}'],
  },
});