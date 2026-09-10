---
title: "Kiefer Waight Projects | AI, Edge, and Platform Systems"
description: "Selected project history across applied AI infrastructure, industrial telemetry, platform modernization, marketplace scaling, and enterprise delivery."
canonical: "https://kieferwaight.com/projects/"
og_title: "Kiefer Waight Projects"
og_description: "A public history of product work, website rescue, applied ML, and enterprise delivery."
og_type: "website"
og_image: "https://images.kieferwaight.com/kiefer-bryan-waight-headshot-og-image.jpg"
author_name: "Kiefer Waight"
schema_type: "CollectionPage"
nav_variant: "content"
schema_name: "Kiefer Waight Projects"
---
# AI, edge, and platform systems

My work spans consumer products, enterprise websites, industrial sensing, and the infrastructure around AI. Across those settings, I focus on how a system fits together: where data moves, who owns each decision, and what a team needs to keep the product running.

These summaries connect each project to a fuller account. The AI architecture essays describe design approaches; the case studies and career records describe project work.

## Applied AI & infrastructure

### Local-first AI: The Cloud Exodus

Running a model locally is one part of building a private AI system. The larger challenge is deciding where requests execute, which machines may receive sensitive context, and what happens when the preferred node is unavailable.

My architecture essay explores a system that distributes inference, retrieval, storage, and preprocessing across different classes of hardware on a private mesh network. It treats workload placement as an explicit policy decision, with defined boundaries for cloud use and fallback behavior. The focus is the operating model around inference: making privacy, capacity, and failure handling understandable before adding more automation.

[Read The Cloud Exodus](/writing/local-first-ai/).

### Custodial secrets and auditable architecture

An automated workflow needs enough visibility to understand a system without gaining unnecessary access to its credentials. This architecture work examines how to separate those responsibilities.

The design places secret custody in OpenBao and delegates narrowly scoped credential handling to isolated runtime processes. It explores volatile mounts, ephemeral sidecars, sanitized outputs, and declarative orchestration, alongside failure cases such as a sealed secret store or a process exceeding its memory limit. The central question is how to make credential use reviewable while keeping sensitive values out of the ordinary repository and agent context.

[Read the custodial secrets architecture](/writing/custodial-secrets-architecture/).

## Telemetry & edge systems

### Industrial telemetry ML system

An industrial compactor already produces signals about its behavior. This project explored how to use those signals to infer fill level without installing an invasive fill-level sensor, then connect that inference to a practical question: when should the asset be serviced?

My work focused on non-invasive sensing, waveform interpretation, feature translation, and the relationship between model output and operational decisions. The case study follows the system from raw signals through modeling, feedback, dispatch, and failure analysis. Synthetic benchmark material and an inference demo support the public explanation, while the narrative addresses the uncertainty and variation that make field telemetry difficult.

[Explore the industrial telemetry case study](/case-studies/industrial-telemetry/) or [read the research brief](/research/telemetry/).

## Platform modernization & enterprise delivery

### University of Texas Arlington website transformation

The UTA Design Site engagement began with an inherited Gatsby, React, Contentful, and Azure DevOps stack. Knowledge of the system was spread across repositories, teams, and undocumented practices, making it difficult to establish a shared view of maintenance and delivery.

As Website Transformation Project Manager, I worked with stakeholders to map the architecture, content flows, environments, and ownership boundaries. The engagement produced setup guidance, dependency and technical-debt inventories, prioritized risks, workflow documentation, and a maintenance roadmap. The handoff gave the team a clearer record of how to work with the site and where future decisions required coordination.

[Read the UTA transformation case study](/case-studies/uta-website-transformation/).

### Andersen Corp web properties

Enterprise web development requires coordination between the interface, the content platform, and the teams responsible for different brands. At Andersen, my role as Senior Front End Developer covered web properties built with React and Next.js, using headless Sitecore JSS for content management and Vercel for hosting.

The work spanned multiple brand properties with their own component libraries and content workflows. It brought together component-based front-end development, CMS integration, and delivery within an established enterprise environment. This experience reflects the day-to-day engineering needed to support distinct web experiences within a shared corporate ecosystem.

[Read the Andersen career account](/archive/andersen-corp/).

### TC Energy pipeline meter portal

At TC Energy, I built and maintained an Angular portal for managing pipeline meter data. The engagement combined interface development with changes to the deployment and authentication workflows supporting the application.

As Senior Angular Developer, I worked on an AWS deployment and authentication overhaul using a multi-repository strategy. I also applied Tailwind CSS to improve styling consistency across teams contributing to the portal. The work connected application behavior, delivery infrastructure, and collaboration with non-technical stakeholders on UI direction.

[Read the TC Energy career account](/archive/tc-energy/).

### Great Wolf Resorts booking integrations

A booking experience depends on the systems behind the page: reservation data, rate calculations, customer communications, and payment-related workflows. As a Development Consultant for Great Wolf Resorts, I built middleware connecting the Opera reservation system to the customer-facing website for rate calculations.

The engagement also included Salesforce Marketing Cloud integration for outbound marketing email transactions and a new gift card processing system for online bookings. The work centered on connecting established business systems to the web experience and supporting the transactions that move between them.

[Read the Great Wolf Resorts career account](/archive/great-wolf-resorts/).

## Geospatial products

### SaraGEO

I co-founded SaraGEO with Sean Narvasa and served as its architect. The platform brought geographic data, media, and location sharing into a common workspace. The project was later handed over to Raf Collado and Sascha Mornell.

The project account records that history alongside the original product presentation.

[Explore SaraGEO and its pitch deck](/archive/sarageo/).

## Marketplace & consumer products

### Vinoez

Photographs from my time exploring Napa Valley with the Vinoez team, including winery production areas, barrel storage, and the surrounding grounds.

[View the Vinoez Napa Valley gallery](/archive/vinoez/).

### CorkSharing

I built the CorkSharing platform, its web and mobile applications, and its API. I also set up the offshore engineering team and traveled through Napa Valley to help establish the product.

The work combined platform engineering with team setup and direct participation in product development on the ground. The project account brings those responsibilities together with public references to CorkSharing and Bryan Petro's marketplace history.

[Read the CorkSharing project account](/archive/corksharing/).

### ZigAir flight-sharing marketplace

ZigAir brought a seat-based booking model to private charter travel, allowing travelers to share the cost of a flight. Founded in 2012, it appears in the AppealingStudio history as an early travel marketplace project.

The historical homepage organized the experience around departure city, destination, travel dates, and seat count, with a separate entry point for listing an aircraft. That interface made the product proposition concrete: search for an individual seat while connecting travelers with charter supply. The project adds aviation and marketplace context to the studio work that preceded GetMyBoat.

[Read the ZigAir project history and sources](/archive/zigair/).

### GetMyBoat

My work as Chief Architect for GetMyBoat sits within a longer history of marketplace development through AppealingStudio. The public archive traces early product and staging work, launch activity, later product storytelling, and collaboration with a distributed engineering team.

The project brought together product engineering and the relationships required to sustain a growing marketplace. The record includes my visit to the Buenos Aires engineering team to strengthen the technical working relationship. The timeline connects those first-person accounts with historical studio material and press coverage so readers can follow the work in context.

[Explore the GetMyBoat timeline](/archive/getmyboat-timeline/).

### Kickback Apps platform development

As Lead Developer at Kickback Apps, I worked across a portfolio of consumer products, including Bellhop and PrankDial. The role combined product development, ongoing application maintenance, media processing, and cloud infrastructure work.

Alongside the individual applications, I worked on a migration to stateless, serverless architecture that reduced AWS operating costs. The portfolio also included video editing and audio merging workflows for recordings. Working across these systems required balancing product delivery with the cost and complexity of the infrastructure supporting it.

[Read the Kickback Apps career account](/archive/kickback-apps/).

### Bellhop

Bellhop was part of my development work at Kickback Apps, spanning React Native, React, AWS services, and a Node.js backend. The application connected mobile and web development with the services needed to support the product.

My role covered Bellhop within the broader consumer-app portfolio. It is a concrete example of full-stack work across client interfaces and backend infrastructure, with the operating responsibilities that come with maintaining an application alongside other products.

[Read the Bellhop context in the Kickback Apps account](/archive/kickback-apps/).

### PrankDial

PrankDial combines a catalog of prerecorded call scenarios with customization, call progress, and recording history. The product spans a public website and a mobile app, with tokens supporting its purchase model.

At Kickback Apps, I spent substantial time programming Asterisk call trees for PrankDial, alongside maintaining prankdial.com and its Express.js API. This work extended from the web application into the call-flow logic behind the telephone experience. My work supported an established consumer product within a broader portfolio of application development, media workflows, and infrastructure improvements. The dedicated project account connects that role to the historical product screens and Fahim Saleh's account of the company's origins.

[Read the PrankDial project account and sources](/archive/prankdial/).

### AppealingStudio

I co-founded AppealingStudio with Melanie Waight and served as CTO. Our partnership paired Melanie's design work with my development work, bringing strategy, web and mobile engineering, and product iteration into one studio.

The historical studio record follows projects from early concepts toward beta and launch. It includes marketplace and product work such as ElectronicPenny, PocketSpheres, PitchBrite, MentionTribe, ZigAir, and GetMyBoat. That history provides the context for my later work across product architecture, client delivery, and distributed engineering teams.

[Explore the AppealingStudio history](/archive/appealingstudio/).

## Publishing & public identity

### Personal website and public career record

This site brings together my resume, project history, technical writing, case studies, and historical sources. The design problem is editorial as much as technical: a reader should be able to move from a concise claim to the work and context behind it.

The implementation uses Astro content collections and Markdown, with shared layouts for page structure and metadata. Related pages connect the professional overview to detailed accounts, while the archive preserves the distinction between historical material and first-person recollection. Canonical URLs, a sitemap, and descriptive internal links support discovery. The result is a maintained body of work that can be read as individual articles or explored as a connected career history.

[Read about the site's content architecture](/writing/seo-public-resume/) or [browse the archive](/archive/).

## Advisory & modernization

The same approach informs my advisory work: understand the existing system, identify the decisions that matter, and leave the team with a usable path forward. Engagements cover architecture and scaling audits, AI integration roadmaps, and infrastructure modernization.

The UTA case study shows how that approach applies to an inherited web platform; the AI essays explain the boundaries I examine around inference and credential handling. [See the advisory engagement model](/advisory/) for the scope, inputs, and deliverables.
