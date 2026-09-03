---
title: "Reading Industrial Behavior as a Time-Series System | Kiefer Waight"
description: "A practical account of cycle segmentation, feature engineering, device fingerprints, site context, and confidence in industrial telemetry."
canonical: "https://kieferwaight.com/case-studies/industrial-telemetry/modeling.html"
og_title: "Reading Industrial Behavior as a Time-Series System"
og_description: "How waveform behavior becomes model-ready evidence without relying on a universal threshold."
og_type: "article"
og_image: "https://kieferwaight.com/assets/img/industrial-telemetry/figure-diagram-compactor-feature-engineering.png"
author_name: "Kiefer Waight"
schema_type: "TechArticle"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-09-01"
date_modified: "2026-09-01"
source_url: "https://github.com/kieferwaight/industrial-telemetry-ml-system"
---
# Reading industrial behavior as a time-series system

There was no direct measurement of fullness. The modeling task was to observe noisy telemetry, isolate meaningful crush cycles, normalize different machines, and convert behavior into a decision that an operations team could understand.

![Feature engineering for compactor telemetry](/assets/img/industrial-telemetry/figure-diagram-compactor-feature-engineering.png)

## Start with the cycle, not the whole stream

A raw telemetry stream is difficult to reason about. A segmented crush cycle gives the system a unit of comparison. Each cycle can be described by its startup transient, resistance onset, sustained-load region, peak, release, and duration.

<figure class="diagram-figure"><img src="/diagrams/case-studies-industrial-telemetry-modeling-md-01.svg" alt="case studies industrial telemetry modeling md 01 architecture diagram" loading="lazy" decoding="async" /></figure>

One early modeling trap was treating a large motor-start spike as evidence of compression resistance. Separating startup handling from sustained-load interpretation reduced false positives caused by activation behavior rather than material resistance.

## Features translate physics into evidence

The model did not need a single magic variable. It needed a group of features that describe different parts of the behavior:

| Feature family | Example evidence | Why it helps |
| --- | --- | --- |
| Load | peak, mean, sustained current | distinguishes transient from persistent effort |
| Timing | duration, peak timing, cycle spacing | captures a slower or increasingly pressured cycle |
| Shape | ramp and release slopes, energy ratios | preserves the structure of the waveform |
| Repetition | retries, short-interval clusters | identifies behavior that persists across attempts |
| Context | device history, site type, recent service | prevents global thresholds from doing too much work |

The important feature is often relative change. A 14-second cycle does not mean the same thing for every machine. A change from 8 to 14 seconds on one device may be more informative than a raw 20-second cycle on another.

## A clean, inspectable feature vector

The public benchmark uses a small, dependency-light feature list. This is the shape of the transformation, shortened to make the boundary visible:

```python
FEATURES = [
    "duration_s",
    "peak_current_a",
    "mean_current_a",
    "area_under_curve_a_s",
    "peak_timing_ratio",
    "ramp_slope_a_per_s",
    "release_slope_a_per_s",
    "early_energy_ratio",
    "compression_variability",
]


def vector(row):
    """Turn one labeled telemetry record into model-ready values."""
    return [float(row["features"][name]) for name in FEATURES]
```

That small function is not the whole system. It shows an important engineering habit: make the transition from an event record to model input explicit, named, and testable.

## Normalize the device before comparing it

Two compactors at the same fullness level can produce dramatically different raw telemetry because of motor configuration, equipment age, hydraulic condition, power supply, container size, installation, and maintenance history.

![Device fingerprint comparison](/assets/img/industrial-telemetry/figure-diagram-device-fingerprint-comparison.png)

The system therefore learns a device fingerprint. It establishes an empty-state baseline, tracks normal runtime distributions, and asks whether a new cycle departs from that device’s own behavior. Site type provides another layer of context: apartments, offices, industrial locations, construction sites, and hospitality environments have different rhythms and different failure patterns.

## Confidence is part of the output

Confidence should decrease when signal variance increases, telemetry is missing, behavior diverges from history, or a known false-positive pattern appears. That lets the operational system distinguish a strong recommendation from a case that needs review.

This is the modeling shift: from “what percentage is this?” to “what state is most plausible, how strong is the evidence, and what should happen next?”

## Continue reading

- [From rules to adaptive models](/case-studies/industrial-telemetry/evolution.html) follows how these features became a learning system.
- [Failure modes and drift](/case-studies/industrial-telemetry/failure-modes.html) covers when the features lie or change meaning.
- [The full case study overview](/case-studies/industrial-telemetry/) links the full public record.
