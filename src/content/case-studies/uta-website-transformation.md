---
title: "University of Texas Arlington Website Transformation | Kiefer Waight Case Study"
description: "Case study of Kiefer Waight's University of Texas Arlington website transformation work across Gatsby, React, Contentful, Azure DevOps, discovery, documentation, and handoff."
canonical: "https://kieferwaight.com/case-studies/uta-website-transformation/"
og_title: "University of Texas Arlington Website Transformation"
og_description: "An inherited web stack case study focused on discovery, documentation, security review, and handoff."
og_type: "article"
og_image: "https://kieferwaight.com/assets/img/kiefer-bryan-waight-headshot-og-image.jpg"
author_name: "Kiefer Waight"
schema_type: "Article"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-08-29"
date_modified: "2026-08-29"
---
The UTA Design Site engagement began with an inherited Gatsby, React, Contentful, and Azure DevOps workflow whose operational knowledge was distributed across teams and incomplete documentation. I worked with UTA stakeholders to map the delivery path, document the environment and ownership boundaries, identify operational risks, and create a clearer foundation for future maintenance and development.

## Context

The site depended on several systems and teams: Contentful for content management, Gatsby and React for the frontend, and Azure DevOps for build and deployment workflows. The technical stack was only part of the challenge. The more important question was how those systems, responsibilities, and undocumented practices fit together in daily operation.

## Challenge

The work began with partial institutional knowledge spread across repositories, tools, habits, and team boundaries. Local setup, content flow, deployment responsibilities, and known technical debt were not represented in one shared operating view. That made maintenance slower and increased the risk that important decisions would remain dependent on individual memory.

<figure class="diagram-figure">
	<img src="/diagrams/case-studies-uta-website-transformation-md-02.svg" alt="Repositories, environments, content flow, deployment process, and team knowledge converge through discovery and documentation into a shared system map, setup guide, and prioritized backlog" loading="lazy" decoding="async" />
	<figcaption>Discovery consolidated distributed technical and institutional knowledge into a shared operating view.</figcaption>
</figure>

## Architecture

The delivery path connected content in Contentful to a Gatsby and React frontend, through Azure DevOps build and deployment processes, and into the published UTA web experience. Documentation formed a shared operational layer across those boundaries: it recorded how the pieces related, where ownership changed, and how a future team could work with the system.

<figure class="diagram-figure">
	<img src="/diagrams/case-studies-uta-website-transformation-md-01.svg" alt="Contentful content flows into a Gatsby and React frontend, through Azure DevOps build and deployment, to the UTA web experience, with documentation spanning each system boundary" loading="lazy" decoding="async" />
	<figcaption>Content, build, deployment, and documentation boundaries in the UTA Design Site workflow.</figcaption>
</figure>

## Approach

The approach combined discovery, system mapping, documentation, risk review, backlog triage, and workflow improvement. I conducted discovery with the UTA team to reconstruct the system's architecture, dependencies, and operating practices. The work focused on making the existing system legible before recommending changes.

<figure class="diagram-figure">
	<img src="/diagrams/case-studies-uta-website-transformation-md-03.svg" alt="Five engagement milestones progress from foundation and shared clarity through control and momentum to ownership" loading="lazy" decoding="async" />
	<figcaption>The engagement progressed from discovery and shared context to documented ownership and a maintenance path.</figcaption>
</figure>

## Discovery and Team Alignment

**September 4-8**

The first week established the working relationship, access, and shared context needed to investigate an inherited system. Discovery with the UTA team reconstructed the system's architecture, dependencies, and operating practices while surfacing the institutional context that was not present in the repositories.

The work established an open communication rhythm and a shared record of what needed to be understood. Fresh review helped reveal the system's shape, while UTA stakeholders supplied the operational context behind existing decisions.

**Focus**

- Establish communication channels, project rituals, access, and decision-making paths.
- Map repositories, environments, dependencies, ownership boundaries, and the flow from Sitecore content to the Design Site.
- Begin a newcomer-oriented guide to local setup, architecture, and common terminology.
- Create an initial backlog that distinguishes urgent risks, quick wins, and longer-term improvements.

**Outcome:** Discovery notes, an initial system map, working agreements, and a backlog separating urgent risks, quick wins, and longer-term improvements.

## System Mapping and Documentation

**September 11-22**

The next milestone turned scattered knowledge into a shared map of the code, content, tools, and deployment responsibilities. Essential information had been distributed across repositories, habits, individuals, and undocumented decisions.

The work produced a documented view of repositories, environment setup, content flows, and deployment responsibilities. Documentation, inventory, and guided walkthroughs made the Design Site understandable enough for informed maintenance decisions.

**Focus**

- Document the current architecture, Gatsby/React components, packages, content flows, Sitecore touchpoints, Contentful models, and Azure DevOps processes.
- Create and validate local-development setup instructions, including required configuration, access, and troubleshooting guidance.
- Inventory features, routes, templates, third-party services, dependencies, licenses, and known technical debt.
- Map user and content-creator journeys, sitemap structure, navigation, and operational handoffs between teams.
- Prioritize risks, bugs, security concerns, and backlog items with UTA stakeholders.

**Outcome:** A shared system map, validated setup guidance, an inventory of dependencies and technical debt, and an agreed-upon set of priorities.

## Standards, Risk Review, and Stabilization

**September 25-October 6**

With the system mapped, the work moved from discovery to control: clear standards, safer workflows, stronger components, and a realistic plan for resolving technical debt.

The assessment documented expectations for code quality, security, ownership, and release readiness, rather than leaving those decisions to be reconstructed during each change.

**Focus**

- Define practical standards for branching, pull requests, reviews, testing, documentation, and release decisions.
- Assess frontend components for compatibility, modularity, responsiveness, accessibility, and maintainability.
- Address high-priority security and performance findings in coordination with the ECM team where responsibilities overlap.
- Document technical debt with severity, impact, recommended resolution, and sequencing.
- Verify Contentful models, API integration, webhooks, publishing behavior, and content-management responsibilities.

**Outcome:** The assessment identified prioritized technical-debt, security, performance, and workflow concerns, with recommended remediation steps.

## Workflow Improvements and Delivery Enablement

**October 9-20**

With a shared understanding and stronger controls in place, the work shifted from diagnosis to delivery enablement. The focus was on prioritized backlog items, reduced friction, and a more predictable deployment path.

The objective was not automation for its own sake. It was to identify where workflow improvements could reduce unnecessary friction and make content, quality, and future maintenance easier to manage.

**Focus**

- Prioritize fixes, improvements, and backlog items for implementation and future delivery.
- Assess Gatsby build and static-generation workflows and document recommended improvements.
- Assess and improve the Azure DevOps pipeline for build, test, deployment, traceability, and repeatability.
- Document staging practices and release-review requirements.
- Identify an appropriate path toward continuous deployment, including any technical or governance constraints that may place full automation outside the initial scope.
- Identify performance opportunities involving asset delivery, caching, compression, lazy loading, and targeted frontend improvements.

**Outcome:** The revised workflow clarified how changes could be reviewed, tested, and promoted through the existing delivery path.

## Knowledge Transfer and Operational Handoff

**October 23-November 3**

The final milestone transferred knowledge, validated operational readiness, and documented a route for continued maintenance and development.

The handoff covered setup, changes, risk evaluation, deployment responsibilities, and the points where an issue crossed team boundaries.

**Focus**

- Complete and validate technical documentation, including local setup, architecture, content processes, deployment procedures, troubleshooting, and operational ownership.
- Prepare handoff and training materials for the lead developer and junior developers.
- Create a maintenance roadmap that separates immediate follow-up work, planned improvements, and future opportunities.
- Document and review staging and production release procedures, rollback considerations, health checks, alerts, security scans, and escalation paths.
- Review accomplishments, unresolved decisions, risks, and next steps with project stakeholders.
- Establish a defined post-handoff support and monitoring period, if included in scope.

**Outcome:** The handoff included setup guidance, process documentation, and a maintenance roadmap intended to support continued internal ownership.

## Deliverables

- Local setup and newcomer-oriented architecture guidance.
- Documentation of repositories, components, packages, content flows, Sitecore touchpoints, Contentful models, and Azure DevOps processes.
- Inventory of routes, templates, third-party services, dependencies, licenses, and known technical debt.
- Prioritized findings covering operational, security, performance, and workflow concerns.
- Recommended standards for branching, reviews, testing, documentation, and release decisions.
- Handoff materials covering maintenance, deployment, troubleshooting, ownership, and follow-up work.

## Outcome

The engagement converted a partially inherited and undocumented delivery workflow into a clearer operational picture: how content moved through the system, where team responsibilities intersected, what risks and technical debt required attention, and what procedures would support future maintenance. The lasting value was not limited to code or configuration changes; it was the documentation, shared context, and delivery guidance that reduced reliance on individual memory.

## What I learned

In inherited systems, discovery is delivery. Before a team can modernize a platform confidently, it needs a common understanding of its architecture, dependencies, ownership boundaries, and deployment path. Clear documentation turns that understanding into an asset that remains useful after the engagement ends.

