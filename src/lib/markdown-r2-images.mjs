import { getR2WebpSrcset } from './r2-image-variants.mjs';

function transformChildren(node) {
    if (!node.children) return;
    node.children = node.children.map((child) => {
        transformChildren(child);
        const srcset = child.type === 'element' && child.tagName === 'img' ? getR2WebpSrcset(child.properties?.src) : null;
        if (!srcset) return child;

        return {
            type: 'element',
            tagName: 'picture',
            properties: {},
            children: [
                {
                    type: 'element',
                    tagName: 'source',
                    properties: { srcset, sizes: '(max-width: 700px) calc(100vw - 4rem), 820px', type: 'image/webp' },
                    children: [],
                },
                {
                    ...child,
                    properties: { ...child.properties, sizes: '(max-width: 700px) calc(100vw - 4rem), 820px', loading: child.properties.loading ?? 'lazy', decoding: 'async' },
                },
            ],
        };
    });
}

export function rehypeR2Images() {
    return (tree) => transformChildren(tree);
}