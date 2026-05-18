import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const RECOMMENDATION = z.enum([
  "use",
  "non-preferred",
  "avoid",
  "use-with-care",
  "contested",
  "evolving",
  "reclaimed-in-community",
]);

const CONFIDENCE = z.enum([
  "VERIFIED",
  "VERIFIED-ARCHIVED",
  "SUMMARY-ONLY",
  "PARTIAL",
  "UNVERIFIED",
]);

const RELATION = z.enum([
  "alternative-form",
  "gendered-form",
  "gendered-or-dated-form",
  "geographic-variant",
  "overlapping-but-distinct",
  "subset-identity",
  "umbrella-for",
  // Catch-all for non-identity-overlap relationships: prejudice
  // against an identity (homophobia → gay), co-occurring concepts
  // (pronouns ↔ transgender), methodological adjacencies. Use when
  // the relationship is real and worth surfacing but doesn't fit
  // any of the identity-overlap categories above.
  "related-concept",
]);

const HOST_POSTURE = z.enum([
  "host-publicly",
  "private-mirror-link-out",
  "link-out-only",
]);

const LIVE_STATUS = z.enum(["live", "offline", "login-gated", "404", "paywalled"]);

const GUIDANCE_ENTRY = z.object({
  org: z.string(),
  org_slug: z.string(),
  year: z.number().int(),
  entry_updated: z.coerce.date().nullable().optional(),
  source_url: z.string().url().nullable().optional(),
  local_archive: z.string().nullable().optional(),
  recommendation: RECOMMENDATION,
  derived_from: z.array(z.string()).optional().default([]),
  quote: z.string().nullable(),
  quote_loc: z.string(),
  paraphrase: z.string(),
  confidence: CONFIDENCE,
});

const RELATED_TERM = z.object({
  slug: z.string(),
  relation: RELATION,
});

const CONTEXT_DATA = z.object({
  label: z.string(),
  claim: z.string(),
  url: z.string().url().nullable().optional(),
  relevance: z.string(),
});

const EXTERNAL_REFERENCE = z.object({
  org: z.string(),
  org_slug: z.string(),
  year: z.number().int(),
  source_url: z.string().url().nullable().optional(),
  local_archive: z.string().nullable().optional(),
  references: z.string(),
  references_url: z.string().url().nullable().optional(),
  note: z.string(),
});

const METHODOLOGICAL_CONTEXT = z.object({
  org: z.string(),
  org_slug: z.string(),
  year: z.number().int(),
  source_url: z.string().url().nullable().optional(),
  local_archive: z.string().nullable().optional(),
  framework: z.string(),
  note: z.string(),
});

const AUDIENCE_NOTE = z.object({
  audience: z.string(),
  note: z.string(),
});

const terms = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/terms" }),
  schema: z.object({
    term: z.string(),
    slug: z.string(),
    aliases: z.array(z.string()).optional().default([]),
    related_terms: z.array(RELATED_TERM).optional().default([]),
    categories: z.array(z.string()).optional().default([]),
    tags: z.array(z.string()).optional().default([]),
    guidance: z.array(GUIDANCE_ENTRY).optional().default([]),
    context_data: z.array(CONTEXT_DATA).optional().default([]),
    external_references: z.array(EXTERNAL_REFERENCE).optional().default([]),
    methodological_context: z.array(METHODOLOGICAL_CONTEXT).optional().default([]),
    audience_notes: z.array(AUDIENCE_NOTE).optional().default([]),
    pronunciation: z.string().optional(),
    last_reviewed: z.coerce.date(),
    created: z.coerce.date(),
    contributors: z.array(z.string()).optional().default([]),
    // Stub flag — lets us publish a placeholder term page during build-out
    stub: z.boolean().optional().default(false),
  }),
});

const sources = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/sources" }),
  schema: z.object({
    org: z.string(),
    org_slug: z.string(),
    work_title: z.string(),
    year: z.number().int(),
    format: z.enum(["PDF", "web", "markdown", "book"]).optional(),
    length_pages: z.number().int().nullable().optional(),
    length_sections: z.number().int().nullable().optional(),
    copyright_holder: z.string().nullable().optional(),
    license: z.string().nullable().optional(),
    source_url: z.string().url().nullable().optional(),
    local_archive: z.string().nullable().optional(),
    host_posture: HOST_POSTURE,
    live_status: LIVE_STATUS,
    added: z.coerce.date().optional(),
    last_checked: z.coerce.date().optional(),
    version_history: z
      .array(
        z.object({
          year: z.number().int(),
          note: z.string(),
          url: z.string().url().nullable().optional(),
        })
      )
      .optional()
      .default([]),
    stub: z.boolean().optional().default(false),
  }),
});

const chapters = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/chapters" }),
  schema: z.object({
    title: z.string(),
    slug: z.string(),
    order: z.number().int().optional(),
    lede: z.string(),
    cross_cutting_principles: z
      .array(
        z.object({
          title: z.string(),
          body: z.string(),
        })
      )
      .optional()
      .default([]),
    term_slugs: z.array(z.string()).optional().default([]),
    stub: z.boolean().optional().default(false),
  }),
});

export const collections = { terms, sources, chapters };
