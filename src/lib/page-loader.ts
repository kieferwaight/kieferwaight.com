import { getEntry } from 'astro:content';

export async function getPageEntry(page: 'advisory' | 'projects' | 'resume') {
  switch (page) {
    case 'advisory':
      return { entry: await getEntry('pages', 'advisory'), section: 'Advisory' };
    case 'projects':
      return { entry: await getEntry('projects', 'index'), section: 'Projects' };
    case 'resume':
      return { entry: await getEntry('pages', 'resume'), section: 'About' };
  }
}