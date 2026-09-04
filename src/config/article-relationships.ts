type RelatedLink = readonly [href: string, label: string];

type ArticleRelationship = {
  relatedCaseStudies: readonly RelatedLink[];
  relatedWriting: readonly RelatedLink[];
};

const defaultRelationship: ArticleRelationship = {
  relatedCaseStudies: [['/case-studies/industrial-telemetry/', 'Industrial Telemetry ML System']],
  relatedWriting: [
    ['/writing/inherited-systems/', 'How I rescue an inherited web system'],
    ['/writing/documentation-as-product/', 'Documentation is part of delivery'],
  ],
};

const relationships: Record<string, ArticleRelationship> = {
  'inherited-systems': {
    relatedCaseStudies: defaultRelationship.relatedCaseStudies,
    relatedWriting: [
      ['/writing/custodial-secrets-architecture/', 'Custodial secrets and auditable architecture'],
      ['/writing/documentation-as-product/', 'Documentation is part of delivery'],
    ],
  },
  'documentation-as-product': {
    relatedCaseStudies: defaultRelationship.relatedCaseStudies,
    relatedWriting: [
      ['/writing/inherited-systems/', 'How I rescue an inherited web system'],
      ['/writing/custodial-secrets-architecture/', 'Custodial secrets and auditable architecture'],
    ],
  },
};

const telemetryRelationship: ArticleRelationship = {
  ...defaultRelationship,
  relatedCaseStudies: [['/case-studies/uta-website-transformation/', 'UTA Website Transformation']],
};

export function getArticleRelationship(entryId: string): ArticleRelationship {
  return entryId.startsWith('industrial-telemetry/')
    ? telemetryRelationship
    : relationships[entryId] ?? defaultRelationship;
}