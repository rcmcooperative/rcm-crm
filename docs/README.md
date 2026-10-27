# RCM-CRM Documentation

## Current architecture (Baserow)

- [Why crm](why-crm.md) — the case for why this tool exists; architecture-agnostic
- [Engagement framework](engagement-framework.md) — Mountain of Engagement, influence/interest, and the frameworks underpinning the CRM's engagement model. **Marked NEEDS REVIEWING** — check with Cass for what specifically needs review before treating this as current
- [Data privacy](data-privacy.md) — generic DPIA template, to be copied and completed per deployment
- [Platform needs assessment](platform-needs-assessment.md) — the full comparison behind choosing Baserow (vs. SharePoint, SeaTable, self-hosted SQL)
- [Schema](baserow/schema.md) — the current data model: five tables, their relationships, field reference
- [Architecture overview](baserow/architecture-overview.md) — system overview: data sources, Web App, self-serve loop, outputs
- [Self hosted vs cloud](baserow/self-hosted-vs-cloud.md) — Baserow Cloud vs. self-hosted Baserow, for deployments where the choice of *platform* is settled but the choice of *hosting* isn't
- [Structure exports](baserow/structure-exports/) — dated snapshots of the live schema, pulled via Baserow's field-definitions API (see Training for the export process)

## Training for Baserow and kumu
- [1: Designing the visualisation](docs/baserow/training/01-designing-the-visualisation.md)
- [2: Entering data](docs/baserow/training/02-entering-data.md)
- [3: Maintinaing your data](docs/baserow/training/03-maintaining-your-data.md)
- [4: Enabling self-serve editing](docs/baserow/training/04-enabling-self-serve-editing.md)
- [5: Downloading your data](docs/baserow/training/05-downloading-your-data.md)
- [6: Managing your visualisation](docs/baserow/training/06-managing-the-visualisation.md)

## Self-hosted SQL architecture (alternative deployment option)

- [README](self-hosted-architecture/README.md) — what this is, and when it's the right choice
- [Architecture self hosted technical](self-hosted-architecture/architecture-self-hosted-technical.md)
- [Architecture self hosted lay summary](self-hosted-architecture/architecture-self-hosted-lay-summary.md)

## Images and diagrams

See `../assets/images/` — PNG renders plus the editable `.drawio` source files. Two of the four diagrams (`data-process-web-app_drawio.xml`, `data-process-self-serve_drawio.xml`) still need tidying and a PNG export before their `<mark>` placeholders in `baserow/architecture-overview.md` can be finalised.
