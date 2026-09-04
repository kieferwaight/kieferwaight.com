const IMAGE_ORIGIN = 'https://images.kieferwaight.com/';
export const R2_IMAGE_WIDTHS = [480, 768, 960, 1440];

export function getR2WebpSrcset(src) {
    if (typeof src !== 'string' || !src.startsWith(IMAGE_ORIGIN)) return null;
    const url = new URL(src);
    const extension = url.pathname.match(/\.[a-z0-9]+$/i)?.[0];
    if (!extension) return null;
    const baseUrl = `${url.origin}${url.pathname.slice(0, -extension.length)}`;
    return R2_IMAGE_WIDTHS.map((width) => `${baseUrl}-w${width}.webp ${width}w`).join(', ');
}