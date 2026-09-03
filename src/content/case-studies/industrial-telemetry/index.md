---
title: "Industrial Telemetry ML System | Kiefer Waight Case Study"
description: "Case study of Kiefer Waight's industrial telemetry ML work covering non-invasive sensing, waveform analysis, synthetic telemetry, and fill-level inference."
canonical: "https://kieferwaight.com/case-studies/industrial-telemetry/"
og_title: "Industrial Telemetry ML System"
og_description: "A public case study of sensing, waveform analysis, synthetic telemetry, and fill-level inference."
og_type: "article"
og_image: "https://kieferwaight.com/assets/img/kiefer-bryan-waight-headshot-og-image.jpg"
author_name: "Kiefer Waight"
schema_type: "TechArticle"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-08-29"
date_modified: "2026-08-29"
---
# Industrial Telemetry ML System

This project sits at the intersection of sensing, machine learning, and operational judgment. It is a case study in turning an ordinary industrial asset into an observable system without adding an invasive fill-level sensor.

The core problem was to make an industrial compaction system more legible by using non-invasive signal collection, waveform analysis, and synthetic telemetry to infer fill-level behavior. The important output was not a chart. It was a better answer to a dispatch question: should this asset be serviced now?

![Fullness inference workflow](/assets/img/industrial-telemetry/figure-diagram-fullness-inference-workflow.png)

## Read the case study in parts

For the full research narrative, see the [Telemetry research brief](/research/telemetry/), structured around the PDF's numbered sections, evidence tables, and applied-ML thesis.

The long-form material is split into pages that keep their own context. A reader can enter at the problem, the signal, the model, the operating workflow, or the failure analysis without needing the PDF open beside the site.

- [The compactor became the sensor](/case-studies/industrial-telemetry/sensing.html) — why indirect measurement was the useful design move.
- [Reading the signal](/case-studies/industrial-telemetry/modeling.html) — cycle segmentation, features, device fingerprints, and confidence.
- [From rules to adaptive models](/case-studies/industrial-telemetry/evolution.html) — how observation, labels, and feedback changed the system.
- [From prediction to dispatch](/case-studies/industrial-telemetry/operations.html) — where telemetry became a workflow rather than an analytics screen.
- [Failure modes and drift](/case-studies/industrial-telemetry/failure-modes.html) — what broke, what the breaks taught, and why adaptation is normal.

## The system in one sentence

> Existing machine behavior became a signal; the signal became a model; the model became decision support.

## Context

The project centered on an industrial system where the value was not just in collecting data, but in interpreting signals that are hard to observe directly.

That meant the work had to account for noisy inputs, operational variation, and the gap between raw telemetry and a human-usable conclusion.

## What I focused on

### Signal shape

I looked at how waveform patterns, sensor response, and surrounding operating conditions could be described without losing useful detail.

### Feature translation

I paid attention to the bridge between a raw signal and the features a model or analyst would actually consume.

### Operational framing

I kept the story tied to what the system needed to support in practice, not just what looked elegant in a notebook or prototype.

## Public project record

The [public industrial telemetry repository](https://github.com/kieferwaight/industrial-telemetry-ml-system) contains the full authored case study, synthetic benchmark material, figures, and a dependency-light inference demo. The site pages are a restructured reading experience, not a replacement for that source record.

## What this project taught me

1. Data quality is part of the product
1. Public explanation matters
1. Prototype thinking still needs structure

## Related pages

- [Projects](/projects/)
- [Deep dives](/writing/)
- [Resume](/resume/)

## Supporting public record

- [Archive](/archive/)
- [GetMyBoat timeline](/archive/getmyboat-timeline/)
- [Case studies](/case-studies/)
