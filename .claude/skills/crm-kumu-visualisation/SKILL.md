---
name: crm-kumu-visualisation
description: Convert RCM Cooperative's Baserow CRM exports (People, Organisations, Communities, Projects, Interactions) into Kumu-ready elements/connections workbooks, for the internal and public network visualisations. Use when Cass asks to build, update, or refresh the Kumu map, mentions "kumu export", or provides new baserow-export-*.xlsx files for this purpose.
---

# CRM to Kumu visualisation

Deterministic Python pipeline. No LLM calls are made on the CRM data at any
point after this skill is invoked — reading, transforming, and writing the
data is pure Python (pandas/openpyxl), consistent with `crm-notes-extraction`
and `crm-email-contacts`.

## What it does

1. Reads the five Baserow exports (People, Organisations, Communities,
   Projects, Interactions) from `private/kumu/baserow-export/`.
2. Builds a Kumu **elements** sheet (one row per Person/Organisation/
   Community/Project — Interactions are not their own nodes, see
   `references/schema.md`) and a **connections** sheet (one row per
   relationship, generically typed: lead, participant, contact, contributor,
   employee, sponsor, funder, child-of, affiliated).
3. Applies the People consent model (`mapping-consent`) plus two profile
   redaction lists (`PERSON_IDENTIFIABLE_FIELDS`, `PERSON_INTERNAL_ONLY_FIELDS`
   in `config.py`) to produce two workbooks:
   - `kumu-import-internal-<date>.xlsx` — full data, real names, RCM
     Cooperative's own internal Kumu map only.
   - `kumu-import-public-<date>.xlsx` — consent-filtered: only people who
     gave public consent appear at all; pseudonymised people get a stable
     hashed label; some fields (notes, backup emails) never appear here
     regardless of consent tier.
4. Writes both to `private/kumu/kumu-input/`, ready to drag-and-drop import
   into Kumu.

## Running it

```
python .claude/skills/crm-kumu-visualisation/scripts/pipeline.py
```

Run from the repo root. See `references/how-to-run.md` for the full
walkthrough and the confirmed-decisions checklist.

## When the schema changes

1. Re-run the read-only field-definitions export for the affected table(s)
   (see `references/how-to-run.md`).
2. Update `scripts/config.py` — the single file holding the column list,
   the edge-field registry, the profile-field lists, and the consent tiers.
   `pipeline.py` itself should not need editing for ordinary schema drift.
3. Re-run the pipeline.

## Known open questions (see references/schema.md and how-to-run.md)

- Two edges are labelled generically as `affiliated`
  (`Community.organisations`, `Project.communities`) because they don't
  cleanly mirror an existing field on the other side.
- People's relationship/edge fields (organisations, communities-lead, etc.)
  aren't filtered by consent tier at all yet — only profile fields are.
- Two planned People fields (`mission-interest`, `mission-influence`) are
  not built yet; once added they must go into `PERSON_INTERNAL_ONLY_FIELDS`.
- People's seven `-user-nominated` fields are excluded from both exports —
  see `schema.md` for the Category A/B reasoning (staging data vs.
  unreviewed-but-real data pending a reviewed-status field that doesn't
  exist in Baserow yet).
