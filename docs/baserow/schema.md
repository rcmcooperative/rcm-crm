# RCM-CRM — Baserow Schema and Data Model

This document describes the current, live data model of the Baserow-based RCM-CRM: five tables (People, Organisations, Communities, Interactions, Projects) and the relationships between them.

<mark>The `structure-exports/2026-09-15/` snapshot below is known to be stale — work on the `crm-kumu-visualisation` skill surfaced at least two schema changes not reflected in it: the `duplicate-check` field appears to have been removed from Organisations, and `communities-contributor-profile` on People is a multiselect (options: communications, engagement, project management, strategic, technical), not a link field as earlier assumed. Fresh field-definitions exports are pending (see `training.md` for the export process) — treat the field reference below as provisional until that refresh lands.</mark>

For the conceptual/ethical rationale behind what this CRM tracks and why, see `why-crm.md` and `engagement-framework.md`.
For the original self-hosted SQL design this schema evolved from, see `self-hosted-architecture/`.

## Table relationships

![Data model diagram — five tables (People, Organisations, Communities, Interactions, Projects) shown with their full set of Link-to-table fields and target tables, colour-coded per table, with development-status ticks/crosses per field](../../assets/images/data-model_drawio.png)

Editable source: `../../assets/images/source/data-process-model_drawio.xml`.

Every table links to every other table (a full mesh), in several cases via more than one distinct link field between the same pair — for example, People↔Projects exists as three separate relationships (leads, contributors, contact), not one generic link.

Adding a link on one side automatically creates/updates the reverse field on the other (confirmed native Baserow behaviour — see `platform-needs-assessment.md`, Table 1).

## Field reference

<mark>Add table: full field list per table (name, type, formula where applicable, linked table), sourced from the structure-exports/ JSON — one table per section (People, Organisations, Communities, Interactions, Projects)</mark>

## Naming conventions

- `name-X` — computed primary field (formula: long name, with abbreviation in parentheses if present)
- `name-X-long` / `name-X-abbreviation` — the two source fields the primary field formula combines
- Relationship fields are named by role where more than one relationship exists between the same table pair (e.g. `people-leads`, `people-contributors`, `people-contacts` — all link Projects to People, but represent distinct roles)
- `sponsor` and `funder` are treated as distinct relationship types where an Organisation connects to Communities/Projects/Interactions

## Known gaps (marked with a red cross on the diagram)

- `communities-organisations-funder`
- `communities-projects-funder`
- `projects-communities-sponsor` / `projects-communities-funder`

<mark>Confirm whether these are genuinely planned additions or should be removed from the diagram if no longer needed</mark>

## Source data for this document

Structure exported via Baserow's read-only field-definitions API (see `training.md` for the export process). Latest export: `structure-exports/2026-09-15/`.
