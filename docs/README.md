# RCM-CRM Documentation

## Current architecture (Baserow)

- `why-crm.md` — the case for why this tool exists; architecture-agnostic
- `engagement-framework.md` — Mountain of Engagement, influence/interest, and the frameworks underpinning the CRM's engagement model. **Marked NEEDS REVIEWING** — check with Cass for what specifically needs review before treating this as current
- `data-privacy.md` — generic DPIA template, to be copied and completed per deployment
- `platform-needs-assessment.md` — the full comparison behind choosing Baserow (vs. SharePoint, SeaTable, self-hosted SQL)
- `baserow/schema.md` — the current data model: five tables, their relationships, field reference
- `baserow/architecture-overview.md` — system overview: data sources, Web App, self-serve loop, outputs
- `baserow/self-hosted-vs-cloud.md` — Baserow Cloud vs. self-hosted Baserow, for deployments where the choice of *platform* is settled but the choice of *hosting* isn't
- `baserow/training.md` — practical findings: keyboard shortcuts, the duplicate-detection automation build, export/import mechanics
- `baserow/structure-exports/` — dated snapshots of the live schema, pulled via Baserow's field-definitions API (see `training.md` for the export process)

## Self-hosted SQL architecture (an alternative deployment option, not the current build)

- `self-hosted-architecture/README.md` — what this is, and when it's the right choice
- `self-hosted-architecture/architecture-self-hosted-technical.md`
- `self-hosted-architecture/architecture-self-hosted-lay-summary.md`

## Images and diagrams

See `../assets/images/` — PNG renders plus the editable `.drawio` source files. Two of the four diagrams (`data-process-web-app_drawio.xml`, `data-process-self-serve_drawio.xml`) still need tidying and a PNG export before their `<mark>` placeholders in `baserow/architecture-overview.md` can be finalised.
