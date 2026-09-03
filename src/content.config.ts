import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const contentSchema = z.object({
  title: z.string(),
  description: z.string().optional(),
  author_name: z.string().optional(),
  date_published: z.coerce.date().optional(),
  date_modified: z.coerce.date().optional(),
  og_image: z.string().optional(),
  schema_type: z.string().optional(),
  canonical: z.string().optional(),
}).passthrough();

export const collections = {
  pages: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/pages' }), schema: contentSchema }),
  writing: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/writing' }), schema: contentSchema }),
  'case-studies': defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/case-studies' }), schema: contentSchema }),
  archive: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/archive' }), schema: contentSchema }),
  projects: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/projects' }), schema: contentSchema }),
  research: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/research' }), schema: contentSchema }),
  timeline: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/timeline' }),
    schema: z.object({
      title: z.string(),
      date: z.coerce.date(),
      summary: z.string(),
      sourceLabel: z.string().optional(),
      sourceUrl: z.string().url().optional(),
      tags: z.array(z.string()).default([]),
      featured: z.boolean().default(false),
    }),
  }),
};
