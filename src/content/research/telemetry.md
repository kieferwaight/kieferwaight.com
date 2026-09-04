---
title: "The Compactor Became the Sensor | Telemetry Research"
description: "An applied machine learning research brief on turning electrical behavior into operational intelligence across a distributed industrial system."
canonical: "https://kieferwaight.com/research/telemetry/"
og_title: "The Compactor Became the Sensor"
og_description: "From electrical signal to dispatch intelligence: an applied machine learning research brief."
og_type: "article"
og_image: "https://images.kieferwaight.com/industrial-telemetry/figure-diagram-fullness-inference-workflow.png"
author_name: "Kiefer Waight"
schema_type: "TechArticle"
date_published: "2026-09-03"
date_modified: "2026-09-03"
source_pdf: "The Compactor Became The Sensor v2"
---

# The compactor became the sensor

## From electrical signal to dispatch intelligence

This research brief examines how an ordinary industrial asset became an observable system. The system did not add a direct fill-level sensor. It learned to interpret electrical and mechanical behavior as evidence about operational state.

![Fullness inference workflow](https://images.kieferwaight.com/industrial-telemetry/figure-diagram-fullness-inference-workflow.png)

> **Research position:** The valuable output was not a percentage-full dashboard. It was a more defensible answer to a dispatch question: should this asset be serviced now?

<div class="diagram-legend" aria-label="Diagram color legend"><span class="legend-telemetry">Telemetry / physical</span><span class="legend-ai">AI / inference</span><span class="legend-advisory">Decision / human</span><span class="legend-healthy">Verified / operating</span><span class="legend-infra">Infrastructure</span></div>

### Deployment scale

| Signal | Meaning |
| --- | --- |
| **1,000+** | customer locations represented in the deployment |
| **46 states** | distributed operating environments |
| **24/7** | industrial telemetry collection |
| **Millions** | signal events available for analysis |

## <span class="section-number">01</span> Executive summary

### <span class="subsection-number">1.1</span> The business problem

Commercial waste operations had a persistent visibility problem. Fixed schedules dispatched too early, manual inspection did not scale, and overflow response arrived after service quality had already degraded.

The constraint was important: fullness was a hidden state. The system needed to estimate it from behavior already produced by the machine, then place that estimate inside a workflow where a person could review and act.

### <span class="subsection-number">1.2</span> The technical strategy

The work followed a sequence of increasingly honest representations: collect the raw event, isolate the crush cycle, describe its shape, normalize it against device history, infer state with confidence, and close the loop with service outcomes.

<figure class="diagram-figure"><img src="/diagrams/research-telemetry-md-01.svg" alt="research telemetry md 01 architecture diagram" loading="lazy" decoding="async" /></figure>

## <span class="section-number">02</span> Core insight

### <span class="subsection-number">2.1</span> Electrical behavior became operational state

The compactor was not a passive container. Every cycle produced a structured interaction between motor, material, operator, and machine condition. That interaction could be treated as a soft sensor: an indirect measurement of a state that was difficult to observe directly.

### <span class="subsection-number">2.2</span> Relative behavior mattered more than absolute values

A single current value did not mean the same thing across every machine. A change relative to the same device's empty-state baseline, recent cycle history, site type, and maintenance condition was more informative than a universal threshold.

![Empty and full waveform comparison](https://images.kieferwaight.com/industrial-telemetry/figure-diagram-empty-vs-full-waveform-overlay.png)

### <span class="subsection-number">2.3</span> Fullness was not the only signal

The same electrical behavior could be explained by dense material, a temporary obstruction, operator habit, mechanical wear, or a delayed service event. A trustworthy system therefore needed to represent competing explanations and reduce confidence when context was weak.

## <span class="section-number">03</span> Technical architecture

### <span class="subsection-number">3.1</span> From collection to inference

The architecture separated raw observation from interpretation. That separation made the system inspectable: analysts could distinguish what the machine emitted, what the feature pipeline derived, and what the model recommended.

![Electromagnetic sensor telemetry flow](https://images.kieferwaight.com/industrial-telemetry/figure-diagram-electromagnetic-sensor-telemetry-flow.png)

### <span class="subsection-number">3.2</span> A research system still needs operational boundaries

The model was one component in a larger evidence chain. Collection, transport, event storage, signal processing, inference, dashboard review, dispatch, haul confirmation, and audit records each carried a different failure mode and ownership boundary.

## <span class="section-number">04</span> Signal modeling

### <span class="subsection-number">4.1</span> Read a crush cycle like a waveform

The useful unit was not the entire stream. It was a segmented cycle with a startup transient, resistance onset, sustained-load region, peak, release, and duration.

<figure class="diagram-figure"><img src="/diagrams/research-telemetry-md-02.svg" alt="research telemetry md 02 architecture diagram" loading="lazy" decoding="async" /></figure>

### <span class="subsection-number">4.2</span> Feature engineering translated physics into evidence

| Feature family | Example evidence | Research value |
| --- | --- | --- |
| Load | peak, mean, sustained current | separates transient effort from persistent load |
| Timing | duration, peak timing, cycle spacing | captures slower or increasingly pressured behavior |
| Shape | ramp, release slope, energy ratio | preserves waveform structure |
| Repetition | retries, short-interval clusters | identifies behavior that persists across attempts |
| Context | device history, site type, recent service | prevents a global threshold from doing too much |

![Feature engineering for compactor telemetry](https://images.kieferwaight.com/industrial-telemetry/figure-diagram-compactor-feature-engineering.png)

## <span class="section-number">05</span> Why this was hard

### <span class="subsection-number">5.1</span> There was no ground-truth sensor

The system could not casually compare its prediction to a perfect label. A service event was evidence, but it was delayed, operationally mediated, and sometimes caused by a reason other than fullness.

### <span class="subsection-number">5.2</span> Every compactor behaved differently

Device fingerprinting was not an optimization detail. It was a prerequisite for credible inference. Empty-state behavior, startup signatures, runtime distributions, and historical resistance patterns established a local baseline.

### <span class="subsection-number">5.3</span> The environment changed continuously

Waste composition changed. Equipment aged. Sites developed different operating rhythms. Connectivity introduced missingness. Drift was therefore part of the research problem, not an edge case after launch.

## <span class="section-number">06</span> Ground truth and labeling

### <span class="subsection-number">6.1</span> The operational world became the labeling system

Human review, haul confirmation, exception handling, invoice auditing, and site history supplied imperfect but meaningful supervision. The system became stronger when it treated those events as part of the dataset rather than as separate administrative work.

### <span class="subsection-number">6.2</span> Confidence made uncertainty actionable

Confidence scoring gave the workflow a third state between “automate” and “ignore”: review. A high-confidence recommendation could move forward. A weak or conflicting signal could remain visible for an account manager without being forced into a false certainty.

## <span class="section-number">07</span> Model evolution

### <span class="subsection-number">7.1</span> From rules to adaptive models

Thresholds were useful because they made assumptions visible. Their failures pushed the system toward segmentation, device fingerprints, site context, trend modeling, and operational feedback.

<figure class="diagram-figure"><img src="/diagrams/research-telemetry-md-03.svg" alt="research telemetry md 03 architecture diagram" loading="lazy" decoding="async" /></figure>

The important evolution was not a claim of model sophistication. It was a change in what the system was willing to admit: behavior is relative, labels are imperfect, and a prediction is only useful when its uncertainty can be carried into the next decision.

## <span class="section-number">08</span> Operational integration

### <span class="subsection-number">8.1</span> Prediction became dispatch support

The model score mattered when it changed a decision. The operational loop connected telemetry collection, inference, review, service scheduling, haul confirmation, and feedback.

![Business outcome dashboard concept](https://images.kieferwaight.com/industrial-telemetry/figure-mockup-business-outcome-dashboard.png)

| Before | After |
| --- | --- |
| Fixed calendar pickup | Behavior-triggered review |
| Manual inspection | Remote telemetry monitoring |
| Reactive overflow response | Earlier risk visibility |
| Opaque distributed asset | Auditable operational context |

## <span class="section-number">09</span> Strategic significance

### <span class="subsection-number">9.1</span> The compactor became an instrument

The central result was a reframing. An industrial asset that had previously been understood through schedules and exceptions became a source of continuous evidence. The system connected physical behavior to a model, the model to a human decision, and the decision to a recorded outcome.

### <span class="subsection-number">9.2</span> Applied machine learning earned authority through the loop

The authority of this work does not come from calling it AI. It comes from the chain of evidence: a measurable signal, an explicit feature representation, a model whose uncertainty is visible, labels grounded in operations, and outcomes that can feed the next iteration.

> **The thesis:** operational intelligence is not the prediction alone. It is the closed loop that makes the prediction explainable, reviewable, and useful.
