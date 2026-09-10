import { describe, expect, it } from 'vitest';
import { isSourceImage, variantKey, verifyPublicUrl } from '../../scripts/upload-images-to-r2.mjs';

describe('isSourceImage', () => {
    it('accepts jpg, jpeg, png, and webp originals', () => {
        expect(isSourceImage('photo.jpg')).toBe(true);
        expect(isSourceImage('photo.jpeg')).toBe(true);
        expect(isSourceImage('photo.png')).toBe(true);
        expect(isSourceImage('photo.webp')).toBe(true);
    });

    it('is case-insensitive on extension', () => {
        expect(isSourceImage('photo.JPG')).toBe(true);
        expect(isSourceImage('photo.WEBP')).toBe(true);
    });

    it('rejects already-generated responsive variants', () => {
        expect(isSourceImage('photo-w480.webp')).toBe(false);
        expect(isSourceImage('photo-w1440.webp')).toBe(false);
    });

    it('rejects non-image keys', () => {
        expect(isSourceImage('document.pdf')).toBe(false);
        expect(isSourceImage('photo')).toBe(false);
        expect(isSourceImage('archive/notes.txt')).toBe(false);
    });

    it('handles nested paths and filenames with dots', () => {
        expect(isSourceImage('archive/2024/my.photo.v2.png')).toBe(true);
        expect(isSourceImage('archive/2024/my.photo.v2-w960.webp')).toBe(false);
    });
});

describe('variantKey', () => {
    it('inserts the width before the extension', () => {
        expect(variantKey('photo.jpg', 480)).toBe('photo-w480.webp');
        expect(variantKey('archive/example.png', 960)).toBe('archive/example-w960.webp');
    });

    it('always outputs a .webp variant regardless of source extension', () => {
        expect(variantKey('photo.jpeg', 1440)).toBe('photo-w1440.webp');
        expect(variantKey('photo.webp', 768)).toBe('photo-w768.webp');
    });

    it('handles filenames with multiple dots', () => {
        expect(variantKey('my.photo.v2.png', 480)).toBe('my.photo.v2-w480.webp');
    });
});

describe('verifyPublicUrl', () => {
    it('retries a transient public URL failure', async () => {
        const fetchImpl = async () => {
            if (fetchImpl.calls++ === 0) throw new TypeError('fetch failed');
            return { ok: true, status: 200 };
        };
        fetchImpl.calls = 0;

        await expect(verifyPublicUrl('archive/photo-w480.webp', {
            attempts: 2,
            delayMs: 0,
            fetchImpl,
        })).resolves.toBeUndefined();
        expect(fetchImpl.calls).toBe(2);
    });

    it('reports the image key after repeated public URL failures', async () => {
        await expect(verifyPublicUrl('archive/photo-w480.webp', {
            attempts: 2,
            delayMs: 0,
            fetchImpl: async () => ({ ok: false, status: 503 }),
        })).rejects.toThrow('Could not verify archive/photo-w480.webp at https://images.kieferwaight.com after 2 attempts: https://images.kieferwaight.com returned 503.');
    });
});
