# Chapter 6: Managing the visualisation

## Table of contents

- [1. Understanding the graph](#1-understanding-the-graph)
  - [1.1. Node types](#11-node-types)
  - [1.2. Edges and interactions](#12-edges-and-interactions)
  - [1.3. Consent-driven visibility and anonymisation](#13-consent-driven-visibility-and-anonymisation)
- [2. Working in Kumu](#2-working-in-kumu)
  - [2.1. Running the export pipeline](#21-running-the-export-pipeline)
  - [2.2. Internal vs published maps](#22-internal-vs-published-maps)
- [3. Future development: internal-only mapping fields](#3-future-development-internal-only-mapping-fields)

---

This chapter describes how your Baserow CRM data becomes a Kumu network visualisation, and how to run and manage that visualisation once it exists. The export itself is produced by the `crm-kumu-visualisation` skill — a deterministic Python pipeline, with no AI model in the data path, consistent with the privacy approach taken for the other CRM skills (see [What we've deliberately not used the API for](02-entering-data.md#93-what-weve-deliberately-not-used-the-api-for) in Chapter 2).

---

## 1. Understanding the graph

### 1.1. Node types

The graph has four node types, drawn from four of the five Baserow tables:

- `People`
- `Organisations`
- `Communities`
- `Projects`

`Interactions` are **not** their own nodes. Rather than appearing as a fifth node type, each Interaction is flattened into metadata on every People, Organisation, Community, and Project node it touches — so an event with ten attendees shows up as a shared piece of history across those ten People nodes (and any linked Organisation/Community/Project nodes), not as an eleventh node of its own.

Each table's identity field (`name-person`, `name-org`, `name-community`, `name-project` — and `name-interaction`, used only for the flattened metadata, since Interactions themselves don't become nodes) maps directly to Kumu's `label`.

**Node sizing** is fixed, not calculated from any CRM field:

| Node type | Size |
|---|---|
| People | 1 |
| Communities | 50 |
| Projects | 50 |
| Organisations | 100 |

<mark>The Organisation/Community boundary, and the Project/other-table boundary, were left open questions when the pipeline was built — the plan was to ship the four-node-type graph as-is and let the visualisation itself inform whether these boundaries need adjusting. Revisit once there's a working graph to look at.</mark>

### 1.2. Edges and interactions

Edges are **generic** — one shared set of edge types applies across every pair of node types, rather than a different edge type per source-table combination (for example, a Person↔Organisation edge and a Person↔Project edge use the same underlying edge vocabulary, rather than each needing its own type). This was a deliberate simplification to keep the pipeline maintainable as more link types get added to the CRM.

### 1.3. Consent-driven visibility and anonymisation

Every export is filtered and (where necessary) anonymised according to each person's `mapping-consent` field on the `People` table (see [Data Privacy](01-designing-the-visualisation.md#2-data-privacy) in Chapter 1) — one of:

- `consent-not-asked`
- `consent-none`
- `consent-internal`
- `consent-public-pseudonymised`
- `consent-public-identifiable`

This filtering happens **in the export script itself**, not upstream in Baserow — Baserow holds one full, unfiltered dataset, and the pipeline decides what each export is allowed to include based on which export it's producing (internal vs. published — see [Internal vs published maps](#22-internal-vs-published-maps) below).

Where anonymisation is needed (`consent-public-pseudonymised`), the pipeline uses a **hashed ID**, with the salt used to generate that hash stored separately from the export itself — so the mapping from hash back to real identity isn't reconstructable from the export alone.

---

## 2. Working in Kumu

### 2.1. Running the export pipeline

The `crm-kumu-visualisation` skill lives under `.claude/skills/crm-kumu-visualisation/` in the CRM repo, alongside the other CRM skills, and follows the same input/output convention:

- **Input:** `private/kumu/baserow-export`, expecting files named `baserow-structure-<Table>-<DATE>.xlsx` — one file per table, exported from Baserow (see [Chapter 5: Downloading your data](05-downloading-your-data.md)).
- **Output:** `private/kumu/kumu-input` — the Kumu-ready elements/connections files, produced by `scripts/pipeline.py`.

<mark>The exact run command and any flags aren't captured in this documentation yet — pull these from the skill's own `references/how-to-run.md` when writing this section up properly, rather than relying on this summary.</mark>

### 2.2. Internal vs published maps

The pipeline can produce more than one export from the same underlying data, depending on which `mapping-consent` levels (see [Consent-driven visibility and anonymisation](#13-consent-driven-visibility-and-anonymisation) above) are included:

- An **internal map** — for RCM Cooperative's own use, showing everything up to and including `consent-internal`, plus anything at the public consent levels.
- A **published map** — for public sharing, showing only `consent-public-pseudonymised` and `consent-public-identifiable`, anonymised as appropriate.

This distinction is also where the fields described in [Future development: internal-only mapping fields](#3-future-development-internal-only-mapping-fields) below will matter once built: some data (like `mission-interest`/`mission-influence`) is intended for the internal map only, and must never appear in a published export, regardless of the row's consent level.

<mark>How the two exports are actually invoked (two separate pipeline runs, a flag, separate config files) isn't yet documented here — confirm against `scripts/config.py` when this section is written up in full.</mark>

---

## 3. Future development: internal-only mapping fields

<mark>Marked for future development, not yet built.</mark>

Two new fields are planned on the `People` table: `mission-interest` and `mission-influence`. These record an administrator's own assessment of a person — how interested they are in RCM Cooperative's mission, and how much influence they have — rather than anything the person has stated about themselves. Because of that, they're a different kind of data to everything else in the `People` table so far:

- They are **opinions held about someone**, not self-disclosed facts, so they sit outside the [`mapping-consent`](01-designing-the-visualisation.md#2-data-privacy) consent framework entirely — a person's consent level doesn't apply to data they never provided or agreed to.
- They must be used **only on the internal Kumu map**, and must **never be exported or published** — including for rows at `consent-public-identifiable`, where every other field on that row is eligible for the public map. Consent to be shown publicly is not consent to have an administrator's assessment of you shown publicly.

When this is built, it will need:

1. The two fields added to the `People` table (see [Amend fields](02-entering-data.md#66-amend-fields) in Chapter 2) — likely Single select or Number, depending on how granular a scale is wanted.
2. An explicit, hard-coded exclusion of both fields from the `crm-kumu-visualisation` export pipeline's published output, so a future change elsewhere in that pipeline (for example, a change to what `consent-public-identifiable` exposes) can't accidentally start including them. This shouldn't rely solely on the consent-level logic described above — since these fields are excluded from *all* exports regardless of consent, not just gated by it — but sit as its own, separate check.
3. This section rewritten once the fields and the exclusion are actually built, rather than left as this flag.
