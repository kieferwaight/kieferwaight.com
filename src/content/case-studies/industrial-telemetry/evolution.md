---
title: "From Rules to Adaptive Models | Kiefer Waight"
description: "How an industrial telemetry system evolved from observation and thresholds into device-aware, confidence-scored, feedback-driven inference."
canonical: "https://kieferwaight.com/case-studies/industrial-telemetry/evolution.html"
og_title: "From Rules to Adaptive Models"
og_description: "Model evolution, ground truth, and the feedback loop behind industrial operational intelligence."
og_type: "article"
og_image: "https://kieferwaight.com/assets/img/industrial-telemetry/figure-diagram-end-to-end-model-evolution-workflow.png"
author_name: "Kiefer Waight"
schema_type: "TechArticle"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-09-01"
date_modified: "2026-09-01"
source_url: "https://github.com/kieferwaight/industrial-telemetry-ml-system"
---
# From rules to adaptive models

The system's job was not simply to classify a container as full or empty. It was to convert noisy electrical telemetry into a confidence-scored operational signal: one that could highlight likely service needs, surface uncertainty for review, and improve as confirmed outcomes accumulated.

It evolved through progressively more honest representations of uncertainty: direct observation, thresholds, segmented cycles, device-specific baselines, trend-aware confidence, and operational feedback.

<figure class="diagram-figure">
    <img src="/assets/img/industrial-telemetry/figure-diagram-end-to-end-model-evolution-workflow.png" alt="Model evolution from raw observation and thresholds through normalized cycles, device behavior, confidence, trend, and service outcomes" loading="lazy" decoding="async" />
    <figcaption>The workflow shifts model output from a binary classification to a confidence-ranked review signal.</figcaption>
</figure>

## The evolution in six moves

<figure class="diagram-figure">
    <img src="/diagrams/case-studies-industrial-telemetry-evolution-md-01.svg" alt="Telemetry model evolution from raw observation and thresholds through segmented cycles, device behavior, confidence, and service outcomes" loading="lazy" decoding="async" />
    <figcaption>Model evolution moves from explicit thresholds toward device-aware, confidence-ranked operational signals.</figcaption>
</figure>

### 1. Observe the machine

The first question was whether a machine's electrical cycle carried a repeatable relationship to container resistance. For each cycle, we examined duration, current or load profile, sustained high-resistance periods, and repeated-crush patterns. These observations created enough signal to continue.

### 2. Test rules, then study their failures

Thresholds are useful as a first instrument because they make assumptions visible. They also fail quickly in physical systems. Dense material, construction debris, operator habits, and device-specific variance can all trigger a high-load event without a full container.

### 3. Make the cycle explicit

Raw telemetry is not yet a training example. Segmentation identified the start and end of a machine cycle; filtering reduced noise; normalization made cycles from the same device comparable despite ordinary variation in timing and amplitude. The result was a behavioral unit that could be inspected, labeled, and compared over time.

### 4. Learn a device fingerprint

Each machine needs its own baseline. The system tracks empty-state behavior, runtime distributions, startup signatures, and historical resistance patterns instead of assuming one global threshold. A device-specific baseline becomes more useful as verified history accumulates. Until sufficient history exists, the system should fall back to conservative rules, show lower confidence, or request review rather than pretend a global model understands a new machine.

### 5. Add confidence and trend

The question changed from “is this cycle full?” to “is this device trending toward a known high-resistance state, and how certain are we?” Confidence was an operational control, not a cosmetic score. High-confidence trend signals could be prioritized; ambiguous cases could be queued for review; low-confidence predictions could be recorded without automatically triggering a service decision.

### 6. Close the loop with outcomes

Pickup confirmations, dump records, service timing, account-manager corrections, and exception notes become imperfect but valuable supervision. A pickup timestamp is not a perfect fullness label, because routing convenience or vendor availability can move service earlier or later than the actual threshold crossing. Feedback entered through dispatch review, technician records, and post-service reconciliation could improve the next iteration without pretending that every service event was ground truth.

<figure class="diagram-figure">
    <img src="/assets/img/industrial-telemetry/figure-diagram-human-feedback-loop.png" alt="Human feedback loop connecting model predictions, operational review, service outcomes, and future model updates" loading="lazy" decoding="async" />
    <figcaption>Service outcomes and human review provide imperfect supervision for the next model iteration.</figcaption>
</figure>

## The public benchmark makes the mechanics legible

The repository includes a small K-nearest-neighbor demo using synthetic data. It is explicitly an educational inference example, not a claim about the production model. Its value is that a reader can see the mechanics without a large framework:

```text
1. Normalize the incoming cycle features.
2. Compare them to previously observed device behavior.
3. Select the nearest comparable examples.
4. Weight their labels by similarity.
5. Return both the prediction and evidence for inspection.
```

The point is not the classifier choice. The point is the boundary: transform a row, compare it with known behavior, return a prediction, and keep enough information to inspect why that prediction happened.

## How the system was evaluated

The model was evaluated as a decision-support system rather than a single offline score. Useful checks included whether predictions aligned with reviewed service outcomes, whether confidence reflected error rates, whether false positives created avoidable work, and whether performance held across devices and site conditions.

The most important question was not whether a model produced a label. It was whether the label improved a real operational decision without hiding uncertainty.

## What the telemetry could not explain alone

Electrical behavior could indicate resistance, but it could not directly determine the material type, confirm whether a pickup was necessary, or explain every unusual cycle. Site context, device condition, routing practices, and human review remained part of the decision system.

## Why the loop matters more than the first model

Every deployment exposed a new edge case. Every false prediction revealed missing context. Every operational interaction generated a new learning opportunity. That makes the dataset more than a collection of waveforms: it combines machine behavior, site history, human review, service timing, and actual outcomes.

The durable system is the feedback loop around the model.

## Continue reading

- [Reading industrial behavior](/case-studies/industrial-telemetry/modeling.html) covers the feature boundary.
- [From prediction to dispatch](/case-studies/industrial-telemetry/operations.html) follows the operational loop.
- [Failure modes and drift](/case-studies/industrial-telemetry/failure-modes.html) shows why adaptation never ends.
