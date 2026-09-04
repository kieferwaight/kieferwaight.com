---
title: "SEO for a Public Resume Site | Kiefer Waight"
description: "How I structure a public resume site so search can connect a name to skills, projects, writing, and technical proof."
canonical: "https://kieferwaight.com/writing/seo-public-resume/"
og_title: "SEO for a Public Resume Site"
og_description: "How to build a public resume site that search engines can understand and trust."
og_type: "article"
og_image: "https://images.kieferwaight.com/kiefer-bryan-waight-headshot-og-image.jpg"
author_name: "Kiefer Waight"
schema_type: "BlogPosting"
nav_variant: "content"
author_type: "Person"
author_url: "https://kieferwaight.com"
date_published: "2026-08-29"
date_modified: "2026-08-29"
---
# SEO for a public resume site

A public resume site is an evidence system, not just a landing page. Its job is to connect a person's name to a clear professional identity, then give each substantial claim a page where a reader can inspect the work behind it.

That is a more useful objective than trying to manufacture authority through page count. Google describes people-first content as useful, reliable, and created to help visitors rather than primarily to manipulate rankings. [Its guidance on creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) is a useful standard for the editorial decisions on this site.

<figure class="diagram-figure">
	<img src="/diagrams/writing-seo-public-resume-md-01.svg" alt="Kiefer Waight identity connects a resume, case studies, and writing to linked evidence for readers, crawlers, and citations" loading="lazy" decoding="async" />
	<figcaption>The site is organized as a connected evidence system: the resume establishes context, case studies substantiate claims, and writing explains the underlying decisions.</figcaption>
</figure>

## Search discovery is a content architecture problem

The target is not a single keyword. It is the relationship between Kiefer Waight, systems architecture, software engineering, applied AI, industrial telemetry, project history, and technical writing.

On this site, the resume establishes the professional overview, case studies substantiate individual claims, and essays document the decisions and methods behind them. Those pages serve different reader intents; they are not near-duplicate keyword targets.

Google's [crawlable links guidance](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) explains that links help crawlers discover pages and use anchor text to understand what linked pages are about. I apply that principle with descriptive internal links such as [industrial telemetry case study](/case-studies/industrial-telemetry/) and [public resume](/resume/), rather than repeating a generic "learn more" label everywhere.

## The site cluster

<figure class="diagram-figure">
	<img src="/diagrams/writing-seo-public-resume-md-02.svg" alt="Homepage identity branches to resume, case studies, and writing, each with distinct supporting evidence" loading="lazy" decoding="async" />
	<figcaption>Distinct pages serve distinct reader intents instead of acting as near-duplicate keyword targets.</figcaption>
</figure>

### Homepage identity

The homepage introduces the name, role, and overall point of view. It links directly to proof: case studies, project history, advisory work, and writing.

### Resume overview

The [resume](/resume/) is intentionally compact. It answers who I am, what I have done, and which capabilities a reader can verify elsewhere.

### Case-study evidence

The [case studies](/case-studies/) move from claims to concrete accounts of architecture, delivery, and operational judgment. Each substantial project has its own durable URL.

### Technical writing

The [writing index](/writing/) provides the reasoning layer: why a decision mattered, what tradeoffs shaped it, and what a reader can carry into another system.

This structure is not a promise of rankings. It is a way to make the site legible to people and to crawlers, while giving each subject enough context to stand on its own.

## Technical implementation

The site uses Astro content collections for the source material and route files for rendering. That separation lets the written content remain authoritative while the route layer supplies consistent metadata and page structure.

The shared layout emits a canonical URL for each page. Canonicals help consolidate a page's preferred address; they do not guarantee indexing or rankings. Google's [canonicalization documentation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) describes them as a signal rather than an absolute command.

The project also generates a sitemap through Astro's sitemap integration. A sitemap is a discovery aid, not a substitute for crawlable navigation. Google's [sitemap documentation](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview) makes the same distinction: it helps search engines find URLs, but inclusion in a sitemap does not guarantee that a URL will be indexed.

The page metadata records the intended content type, author, publication date, and identity relationships. Where structured data is appropriate, the vocabulary should follow [Schema.org](https://schema.org/) and the implementation should be checked against Google's [structured data guidelines](https://developers.google.com/search/docs/appearance/structured-data/intro). Metadata should describe what the page actually contains, not what would be most flattering in a search result.

```json
{
	"@context": "https://schema.org",
	"@type": "Article",
	"headline": "SEO for a Public Resume Site",
	"author": {
		"@type": "Person",
		"name": "Kiefer Waight",
		"url": "https://kieferwaight.com/resume/"
	},
	"datePublished": "2026-08-29",
	"mainEntityOfPage": {
		"@type": "WebPage",
		"@id": "https://kieferwaight.com/writing/seo-public-resume/"
	}
}
```

The excerpt is intentionally small and sanitized. Structured data should describe the page that exists - its article type, author, date, and canonical identity - rather than make unsupported claims about expertise or outcomes.

## Evidence and authorship

Search visibility is downstream of editorial trust. Clear authorship, dates, first-hand explanations, and links to supporting work make it easier for a reader to evaluate a claim. They also make the site's purpose clearer to systems that extract and summarize pages.

That is why the case studies use a byline and publication date, while the essays explain their reasoning instead of presenting a list of disconnected SEO tactics. The work is the evidence. The page structure helps readers reach it.

## External links are part of the argument

Linking to official documentation does not weaken this article. It makes the boundary between general guidance and my own implementation visible. Google's [guidance on crawlable links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) and [outbound-link qualification](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) supports ordinary followed links for editorial citations. `sponsored` belongs on paid placements, `ugc` on applicable user-generated links, and `nofollow` where I do not want to associate the site with a destination.

I do not open citations in a new tab by default. The link should support the reader's investigation without turning every paragraph into a collection of detached browser tasks.

## What I avoid

| Weak pattern | Evidence-first alternative |
| --- | --- |
| Repeating keywords | Explain a real decision with specifics. |
| Creating near-duplicate pages | Publish a distinct page when the subject or reader need is distinct. |
| Writing for a ranking signal | Write for a reader who needs context, proof, and a next step. |

## Limits

Canonical URLs, sitemaps, descriptive links, metadata, and structured data improve discovery and interpretation. None of them guarantees a ranking, a citation in an AI answer, or a click from a search result.

The durable strategy is simpler: publish useful work, give it a clear home, connect related evidence with meaningful links, and describe the implementation honestly. On this site, that means a resume for the overview, case studies for proof, and essays for the reasoning behind the work.

## Sources / Further reading

- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) - Google's guidance on usefulness, experience, and editorial purpose.
- [SEO Starter Guide: Make your links crawlable](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) - link discovery and descriptive anchor text.
- [Qualify outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links) - when to use `sponsored`, `ugc`, or `nofollow`.
- [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview) - sitemap purpose and limits.
- [Consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) - canonical URL signals.
- [Structured data intro](https://developers.google.com/search/docs/appearance/structured-data/intro) - Google's implementation guidance.
- [Schema.org](https://schema.org/) - the shared vocabulary used to describe entities and content.
