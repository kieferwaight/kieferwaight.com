import { describe, expect, it } from 'vitest';
import { getArticleRelationship } from '../../src/config/article-relationships';

describe('article relationships', () => {
  it('uses the telemetry-specific case-study relationship', () => {
    const relationship = getArticleRelationship('industrial-telemetry/modeling');

    expect(relationship.relatedCaseStudies).toEqual([
      ['/case-studies/uta-website-transformation/', 'UTA Website Transformation'],
    ]);
  });

  it('uses the documented writing relationships', () => {
    const relationship = getArticleRelationship('documentation-as-product');

    expect(relationship.relatedWriting.map(([href]) => href)).toEqual([
      '/writing/inherited-systems/',
      '/writing/custodial-secrets-architecture/',
    ]);
  });

  it('falls back for unknown entries', () => {
    const relationship = getArticleRelationship('unknown-entry');

    expect(relationship.relatedCaseStudies[0][0]).toBe('/case-studies/industrial-telemetry/');
    expect(relationship.relatedWriting).toHaveLength(2);
  });
});