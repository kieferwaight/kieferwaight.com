---
title: "SaraGEO | Collaborative Mapping Platform and Founding Architecture"
display_title: "SaraGEO"
description: "A founder archive of SaraGEO, a collaborative mapping platform for geographic data, media, and live location sharing."
canonical: "https://kieferwaight.com/archive/sarageo/"
og_title: "SaraGEO: Collaborative Mapping Platform and Founding Architecture"
og_description: "Kiefer Waight co-founded SaraGEO with Sean Narvasa and served as its architect. This archive documents the 2015 product deck, platform decisions, and later handover."
og_type: "article"
og_image: "https://kieferwaight.com/assets/img/sarageo/product-introduction.jpg"
author_name: "Kiefer Waight"
schema_type: "Article"
nav_variant: "content"
author_type: "Person"
photo_gallery: "sarageo"
---

## Overview

SaraGEO was a collaborative mapping platform for bringing geographic data, media, and live location information into a shared map workspace. Its September 2015 product deck describes a product built around map creation, imported data, visualization, location sharing, and remote collaboration.

I co-founded SaraGEO with Sean Narvasa and served as its architect. My role was to give the product a technical direction that could connect those capabilities into one coherent system. The project was later handed over to Raf Collado and Sascha Mornell.

This is a founder archive, not a claim of a verified commercial launch or current operation. It preserves the available product artifact, the platform model it presented, and the limits of the public record.

## My role

As co-founder and architect, I owned the product's technical direction: shaping how mapping, data, location, and collaboration needed to relate before they could be presented as a usable platform.

The public deck does not assign individual screens, integrations, endpoints, or implementation tasks to a particular founder. For that reason, this page distinguishes my confirmed founding and architectural ownership from the product capabilities described in the deck. It does not claim a specific technology stack, a production deployment, or individual feature implementation that the available artifacts cannot substantiate.

## The system in plain language

The deck presents SaraGEO as three connected product layers:

| Product layer | What the deck describes |
| --- | --- |
| **Map workspace** | Basemaps, pins, notes, drawing tools, media attachments, and on-demand layers. |
| **Data and visualization** | File imports, remote database imports, third-party APIs, and map views such as points, clusters, and heatmaps. |
| **Location and collaboration** | Live location updates, scoped visibility, role-based access, comments, direct messages, and shared map updates. |

The important architectural idea was not a map in isolation. It was a workspace where information could be attached to places, interpreted visually, and shared with the people who needed to act on it.

## Key product decisions visible in the record

### Make the map an active workspace

The product deck treats the map as a place to add context, rather than a static view. Pins, notes, drawn shapes, media, and layers make the map a working surface for information that changes over time.

### Bring data into the product instead of leaving it in source systems

The deck describes shape, CSV, and XLS imports, database imports, third-party integrations, and visualizations such as heatmaps and clusters. That framing makes ingestion and interpretation part of the product experience, not a separate analyst-only process.

### Pair live location with deliberate visibility boundaries

The location-sharing material describes real-time updates alongside a choice of who can see whom and the ability to stop sharing. The collaboration material adds role-based authentication and direct interaction around map items. Together, those slides show that coordination and access scope were meant to be designed together.

## Evidence and status

| Period | Record |
| --- | --- |
| Before September 2015 | Sean Narvasa and I co-founded SaraGEO; I served as architect. This is my first-person account. |
| September 2015 | The 12-slide product introduction documents the platform concept, its feature set, and a developer API proposal. |
| Later | The project was handed over to Raf Collado and Sascha Mornell. This is my first-person account. |
| Current archive status | This page preserves the product record. It does not establish operation, customer adoption, revenue, uptime, or feature availability after the handover. |

The developer API slide presents more than 150 secured RESTful endpoints across maps, data, location, and social features, backed by a geospatial data store. That is evidence of the platform's intended API scope. It is not evidence, on its own, of a particular implementation stack or production performance.

## Original product deck

<figure>
  <a href="/decks/sarageo-product-introduction-2015.pdf"><img src="/assets/img/sarageo/product-introduction.jpg" alt="SaraGEO product introduction cover showing a mobile phone, September 2015" width="320" height="180" loading="eager" decoding="async" /></a>
  <figcaption>Product Introduction, September 2015. Select the cover to open the complete deck.</figcaption>
</figure>

[Open the complete deck (PDF, 12 slides, 13 MB)](/decks/sarageo-product-introduction-2015.pdf) or <a href="/decks/sarageo-product-introduction-2015.pdf" download="SaraGEO-Product-Introduction-2015.pdf">download a copy</a>.

<iframe src="/decks/sarageo-product-introduction-2015.pdf" title="SaraGEO product introduction — complete 12-slide PDF" width="100%" height="600" loading="lazy" style="display: block; max-width: 100%; border: 1px solid #aaa; border-radius: 8px;"></iframe>

If the viewer is unavailable in your browser, use the PDF link above. The [original SlideShare presentation](https://www.slideshare.net/slideshow/sarageo-mapping-platform/52729335) is also available.

## Why this is archived

SaraGEO belongs in this portfolio because it records an early founder and architecture problem: turning a broad set of geospatial, data, and collaboration capabilities into a product model that a team could explain and build toward. The deck is useful evidence of the system boundary and product decisions, even where the public record does not support stronger claims about later outcomes.

## Sources

- [Original SaraGEO product introduction PDF](/decks/sarageo-product-introduction-2015.pdf) — complete deck supplied by Kiefer Waight.
- [SaraGEO Mapping Platform on SlideShare](https://www.slideshare.net/slideshow/sarageo-mapping-platform/52729335) — original public product presentation.
- [SaraGEO on Crunchbase](https://www.crunchbase.com/organization/sarageo) — supplied company reference; access was blocked during preparation and its contents are not used here.

[Return to all projects](/projects/).
