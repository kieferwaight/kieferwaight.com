import { describe, expect, it } from 'vitest';
import { getR2WebpSrcset, R2_IMAGE_WIDTHS } from '../../src/lib/r2-image-variants.mjs';

describe('R2 image variants', () => {
  it('derives standard responsive candidates from any R2 image URL', () => {
    const srcset = getR2WebpSrcset('https://images.kieferwaight.com/archive/example.jpg');

    expect(srcset).toBe(R2_IMAGE_WIDTHS.map((width) => `https://images.kieferwaight.com/archive/example-w${width}.webp ${width}w`).join(', '));
  });

  it('preserves the path and ignores query strings when deriving variants', () => {
    const srcset = getR2WebpSrcset('https://images.kieferwaight.com/a/photo.png?version=2');

    expect(srcset).toContain('/a/photo-w480.webp 480w');
    expect(srcset).not.toContain('version=2');
  });

  it('does not transform non-R2 URLs or extensionless URLs', () => {
    expect(getR2WebpSrcset('https://example.com/photo.jpg')).toBeNull();
    expect(getR2WebpSrcset('https://images.kieferwaight.com/photo')).toBeNull();
  });
});