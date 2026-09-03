---
title: "Documentation Should Follow the Code | Kiefer Waight"
description: "Why documentation should follow the code as a generated, reviewable snapshot of system evidence, with human context added where the repository cannot speak for itself."
canonical: "https://kieferwaight.com/writing/documentation-as-product/"
og_title: "Documentation Should Follow the Code"
og_description: "Why documentation, onboarding, and handoff materials should be treated as product deliverables."
og_type: "article"
og_image: "https://kieferwaight.com/assets/img/kiefer-bryan-waight-headshot-og-image.jpg"
author_name: "Kiefer Waight"
schema_type: "BlogPosting"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-08-29"
date_modified: "2026-08-29"
---
# Documentation Should Follow the Code

Documentation becomes unreliable when it is maintained as a second system beside the code. The repository changes through commits, tests, schemas, configuration, and review; the prose often changes later, if at all.

A better model is to treat documentation as a generated and verified snapshot of the system. Code, tests, and configuration are the source of truth. Documentation should explain only what a reader cannot efficiently infer from that evidence.

> Generate what the repository proves, and write prose where the repository cannot explain intent.

This does not mean an agent should produce pages of confident prose about every directory and function. It means agents can turn repository evidence into a useful map, flag uncertainty, and keep human-authored context attached to the code it explains.

## The problem with parallel truth

Manual documentation drifts because it changes at a different speed and through a different review path than the system it describes. A renamed command can leave a setup guide broken. A changed route can make an architecture diagram misleading. A new configuration key can remain invisible until someone discovers it during an incident.

The problem is not that people write documentation. The problem is treating prose as an independent authority when the repository already contains stronger evidence.

## Code is the primary source

Types, interfaces, tests, routes, configuration, schemas, CLI help, and meaningful names describe system mechanics more accurately than a paraphrase can. They are closer to execution, versioned with the change, and available to automated checks.

That does not make every codebase self-explanatory. It establishes a useful boundary: generate what the repository proves, and write prose where the repository cannot explain intent.

## Generate a snapshot

Tools such as Shdoc are most useful as documentation compilers or repository interrogators, not as prose generators. Their value is the structured snapshot they can anchor in actual artifacts: package metadata, scripts, source trees, types, tests, environment examples, service definitions, and recent changes.

That snapshot gives reviewers a constrained surface to inspect. Instead of asking an agent to "write docs for this project," ask what the repository proves today, what changed since the last snapshot, and which claims require human judgment.

A useful snapshot can describe commands, modules, dependencies, configuration, interfaces, operational paths, and change history. It should be versioned, diffable, and narrow enough that a reviewer can tell why it changed.

## What agents should do

An agentic documentation workflow should be explicit and reviewable:

1. A pull request changes code, tests, schemas, scripts, or configuration.
2. Shdoc regenerates the affected repository snapshot.
3. An agent compares the snapshot with the existing documentation.
4. The agent proposes a narrow patch and links each generated claim to evidence.
5. It flags claims that cannot be substantiated from the repository.
6. CI validates commands, examples, links, and generated artifacts.
7. A human reviews rationale, ownership, security posture, and operational judgment.

The guardrails matter as much as the generation step:

- Ground every generated claim in a file, symbol, test, configuration key, command output, or versioned decision record.
- Treat uncertainty as output. Say "not established by repository evidence" instead of inventing an architectural explanation.
- Generate narrow diffs. Update only documentation affected by the code change.
- Validate executable instructions in CI or a disposable environment.
- Require human review for intent, security posture, ownership, product behavior, and operational risk.
- Measure staleness by flagging references to symbols, commands, files, or configuration that no longer exist.

## What humans must still write

Grounded in repository evidence, an agent can synthesize what exists. It cannot establish why the system exists, who has authority, or which tradeoff matters most.

Architecture rationale, business context, ownership boundaries, incident judgment, operational escalation, and intentional deviations from conventional design require human authorship. Those statements should still be attached to the evidence they explain and reviewed when that evidence changes.

| System knowledge | Primary owner | Documentation approach |
| --- | --- | --- |
| Public APIs, types, routes, and schemas | Code and generated artifacts | Generate from source and validate in CI. |
| Installation and routine commands | Scripts, package metadata, and CLI help | Generate or test commands against a clean environment. |
| Expected behavior | Tests and fixtures | Link documentation to executable examples. |
| Architecture rationale | Humans | Write short decision records with context and tradeoffs. |
| Operational recovery | Humans plus observed operations | Maintain runbooks, but validate commands and ownership regularly. |
| Business intent and constraints | Humans | Write explicitly; agents cannot infer intent from code alone. |

## Prefer no documentation to wrong documentation

Documentation should not narrate obvious code. If a function needs a paragraph to explain what it does, the first question is whether its name, inputs, types, boundaries, or tests can be improved.

Prefer a clear name such as `rotateExpiredServiceCredentials()` over a comment that explains a vague name such as `processKeys()`. Prefer a typed configuration schema over a page listing possible environment variables. Prefer an executable example over instructions that a reader cannot verify.

Write prose when it carries information the code cannot: why a boundary exists, what tradeoff was chosen, who owns a risky operation, what must happen during failure, or what context a future maintainer would otherwise have to rediscover.

### Example: a renamed command

A pull request renames `npm run ingest` to `npm run telemetry:ingest` and updates its script definition. The documentation workflow detects the changed package script, regenerates the command reference, finds the old command in the setup guide, and proposes a focused replacement. If the guide also claims the command performs a nightly backfill but the repository does not establish that behavior, the agent flags the statement for human review instead of preserving it as fact.

## A hierarchy of evidence

1. **Executable truth:** Code, types, schemas, tests, scripts, CI, and runtime configuration.
2. **Generated map:** Repository inventory, dependency relationships, interfaces, command reference, and change-aware summaries.
3. **Human context:** Decisions, tradeoffs, ownership, operational escalation, constraints, and non-obvious failure modes.
4. **Discarded prose:** Duplicated API descriptions, stale setup instructions, commentary on obvious code, and broad claims without evidence.

The goal is not more documentation. It is less unsupported prose and more trustworthy context.

## Verification is the product

Documentation quality is not length or polish. It is traceability: can each important claim be linked to code, configuration, an automated check, or an explicitly named owner?

For this site, that means treating content files, route definitions, schemas, generated diagrams, and build checks as inspectable evidence. A public system with linked decisions, tested commands, and generated repository context is stronger evidence of engineering practice than polished documentation alone.

The standard is not whether a repository has extensive documentation. It is whether a capable person can determine what the system does, verify it, change it safely, and locate the reasoning that code alone cannot convey.

Agents can keep the map current by generating snapshots, surfacing drift, and exposing unsupported claims. They should not become a second source of truth. When the code, tests, and names already explain the system, let them. Document the decisions and constraints that only people can provide.
