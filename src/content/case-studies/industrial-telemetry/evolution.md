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

The system was not built as one finished model. It evolved through increasingly honest representations of uncertainty: first observation, then thresholds, then segmented signals, device fingerprints, site context, trend modeling, and operational feedback.

![End-to-end model evolution workflow](/assets/img/industrial-telemetry/figure-diagram-end-to-end-model-evolution-workflow.png)

## The evolution in six moves

<figure class="diagram-figure"><img src="/diagrams/case-studies-industrial-telemetry-evolution-md-01.svg" alt="case studies industrial telemetry evolution md 01 architecture diagram" loading="lazy" decoding="async" /></figure>

### 1. Observe the machine

The first question was whether electrical behavior visibly changed as fullness increased. Stable short cycles, longer sustained resistance, and repeated crushes created enough signal to continue.

### 2. Test rules, then study their failures

Thresholds are useful as a first instrument because they make assumptions visible. They also fail quickly in physical systems. Dense material, construction debris, operator habits, and device-specific variance can all trigger a high-load event without a full container.

### 3. Make the cycle explicit

Segmentation, noise reduction, waveform normalization, and temporal event analysis turned a continuous signal into comparable evidence. This was the point where “a reading” became “a behavior.”

### 4. Learn a device fingerprint

Each machine needs its own baseline. The system tracks empty-state behavior, runtime distributions, startup signatures, and historical resistance patterns instead of assuming one global threshold.

### 5. Add confidence and trend

The question changed from “is this cycle full?” to “is this device trending toward a known high-resistance state, and how certain are we?” That distinction makes room for review instead of forcing an uncertain prediction into a binary action.

### 6. Close the loop with outcomes

Pickup confirmations, dump records, service timing, account-manager corrections, and exception notes become imperfect but valuable supervision. A pickup timestamp is not a perfect fullness label, because routing convenience or vendor availability can move service earlier or later than the actual threshold crossing.

![Human feedback loop](/assets/img/industrial-telemetry/figure-diagram-human-feedback-loop.png)

## The public benchmark makes the mechanics legible

The repository includes a small K-nearest-neighbor demo using synthetic data. It is explicitly an educational inference example, not a claim about the production model. Its value is that a reader can see the mechanics without a large framework:

```python
def predict_one(self, row):
    vec = self._scale_one(row)
    scored = []
    for train_row, train_vec in zip(self.train_rows, self.train_vectors):
        distance = math.sqrt(
            sum((vec[j] - train_vec[j]) ** 2 for j in range(len(vec)))
        )
        scored.append((distance, train_row["labels"][self.label_key]))

    neighbors = sorted(scored, key=lambda item: item[0])[: self.k]
    return weighted_vote(neighbors)
```

The point is not the classifier choice. The point is the boundary: transform a row, compare it with known behavior, return a prediction, and keep enough information to inspect why that prediction happened.

## Why the loop matters more than the first model

Every deployment exposed a new edge case. Every false prediction revealed missing context. Every operational interaction generated a new learning opportunity. That makes the dataset more than a collection of waveforms: it combines machine behavior, site history, human review, service timing, and actual outcomes.

The durable system is the loop around the model.

## Continue reading

- [Reading industrial behavior](/case-studies/industrial-telemetry/modeling.html) covers the feature boundary.
- [From prediction to dispatch](/case-studies/industrial-telemetry/operations.html) follows the operational loop.
- [Failure modes and drift](/case-studies/industrial-telemetry/failure-modes.html) shows why adaptation never ends.
