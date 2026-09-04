const IMAGE_ORIGIN = 'https://images.kieferwaight.com/';
const WIDTHS_BY_PATH = {
    'getmyboat/buenos-aires-caminito.jpg': [480, 768, 960, 1440],
    'getmyboat/buenos-aires-street-art.jpg': [480, 768, 960],
    'getmyboat/buenos-aires-team.jpg': [480, 768, 960],
    'industrial-telemetry/figure-diagram-compactor-feature-engineering.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-diagram-device-fingerprint-comparison.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-diagram-electromagnetic-sensor-telemetry-flow.png': [480, 768, 960],
    'industrial-telemetry/figure-diagram-empty-vs-full-waveform-overlay.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-diagram-end-to-end-model-evolution-workflow.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-diagram-fullness-inference-workflow.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-diagram-human-feedback-loop.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-diagram-site-type-waveform-overlay.png': [480, 768, 960, 1440],
    'industrial-telemetry/figure-mockup-business-outcome-dashboard.png': [480, 768, 960, 1440],
    'kiefer-bryan-waight-banner-production-log.png': [480, 768, 960],
    'kiefer-bryan-waight-headshot-og-image.jpg': [480, 768],
    'kiefer-bryan-waight-headshot.jpg': [480, 768],
    'kiefer-bryan-waight-headshot.transparent.png': [480, 768],
};

export function getR2WebpSrcset(src) {
    if (typeof src !== 'string' || !src.startsWith(IMAGE_ORIGIN)) return null;
    const path = src.slice(IMAGE_ORIGIN.length);
    const extension = path.match(/(\.[a-z0-9]+)(?:\?.*)?$/i)?.[1];
    const widths = WIDTHS_BY_PATH[path];
    if (!extension || !widths) return null;
    const baseUrl = src.slice(0, -(extension.length));
    return widths.map((width) => `${baseUrl}-w${width}.webp ${width}w`).join(', ');
}