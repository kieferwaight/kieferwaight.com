---
title: "The Compactor Became the Sensor | Kiefer Waight"
description: "How industrial compactor behavior became a non-invasive signal for fullness inference and operational decision support."
canonical: "https://kieferwaight.com/case-studies/industrial-telemetry/sensing/"
og_title: "The Compactor Became the Sensor"
og_description: "A practical case study in indirect measurement, industrial telemetry, and machine behavior."
og_type: "article"
og_image: "https://images.kieferwaight.com/industrial-telemetry/figure-diagram-electromagnetic-sensor-telemetry-flow.png"
author_name: "Kiefer Waight"
schema_type: "TechArticle"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-09-01"
date_modified: "2026-09-01"
source_url: "https://github.com/kieferwaight/industrial-telemetry-ml-system"
---
# The compactor became the sensor

The visible problem was simple: a commercial compactor needed service at the right time. The available choices were not simple. Fixed schedules over-serviced some locations, manual inspection did not scale, and waiting for overflow made the operation reactive.

The useful design move was to stop assuming that fullness had to be measured directly. The machine already produced electrical and mechanical behavior whenever it ran. That behavior could become an indirect measurement of the state inside the container.

![Non-invasive electromagnetic sensing and telemetry flow](https://images.kieferwaight.com/industrial-telemetry/figure-diagram-electromagnetic-sensor-telemetry-flow.png)

## The sensing problem

A traditional fill-level sensor tries to observe the material directly. This system approached the problem as a soft sensor: infer a hidden state from signals that are already available.

That distinction changed the shape of the work. The system did not need to claim that a current value literally meant a percentage full. It needed to learn whether the pattern of a crush cycle was becoming more consistent with resistance, sustained load, repeated attempts, and a history of service events.

<figure class="diagram-figure"><img src="/diagrams/case-studies-industrial-telemetry-sensing-md-01.svg" alt="case studies industrial telemetry sensing md 01 architecture diagram" loading="lazy" decoding="async" /></figure>

## What the machine already tells us

The public case study describes a cycle as a structured event rather than an undifferentiated stream. Useful observations include:

- startup current and the initial transient
- the ramp into compression resistance
- sustained load and peak behavior
- total cycle duration
- the spacing and repetition of cycles
- changes relative to the same device's history

An empty machine tends to produce a shorter, smoother, lower-resistance cycle. A fuller machine can show earlier resistance, longer sustained load, distorted waveform shape, or repeated crush attempts. None of those observations is a complete answer by itself. Together, they form evidence.

![Empty and full waveform comparison](https://images.kieferwaight.com/industrial-telemetry/figure-diagram-empty-vs-full-waveform-overlay.png)

## A useful boundary around the claim

This was not a camera looking into a container, and it was not a universal formula that mapped one number to one fullness percentage. The system inferred an operational state from behavior.

That state could be expressed as a recommendation with a confidence level:

```json
{
  "asset": "compactor-042",
  "state": "approaching_capacity",
  "recommendation": "review_for_service",
  "confidence": 0.89,
  "evidence": [
    "sustained_resistance",
    "longer_cycle_duration",
    "repeated_cycles"
  ]
}
```

The contract is intentionally operational. A person can review it, a dispatch workflow can consume it, and a later service event can provide feedback.

## Why the indirect approach mattered

Indirect measurement reduced the need for invasive retrofit work, but it increased the importance of context. Two machines with similar fullness could produce different raw traces. The same machine could also behave differently after maintenance, during a seasonal occupancy change, or when the waste composition changed.

The central problem therefore became normalization. The question was not “does this value exceed a global threshold?” It was “is this cycle unusual for this compactor, at this site, in this operating context?”

## Continue reading

- [Reading the signal](/case-studies/industrial-telemetry/modeling/) explains how cycles become features.
- [From rules to adaptive models](/case-studies/industrial-telemetry/evolution/) follows the learning loop.
- [From prediction to dispatch](/case-studies/industrial-telemetry/operations/) shows how inference becomes action.

The full public source is the [industrial telemetry ML system repository](https://github.com/kieferwaight/industrial-telemetry-ml-system).
