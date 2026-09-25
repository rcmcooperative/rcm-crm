# Baserow — self-hosted vs. Cloud

`platform-needs-assessment.md` compares Baserow against SharePoint, SeaTable, and the original self-hosted SQL design, and recommends Baserow generally. This document goes one level deeper: once Baserow is the chosen platform, should a given deployment run on **Baserow Cloud** (what RCM Cooperative's own CRM currently uses) or **self-hosted Baserow**?

Both options give access to the same core, open-source feature set — the difference is who runs the infrastructure, and what that trades off.

## Deployment

| | Baserow Cloud | Self-hosted Baserow |
|---|---|---|
| Setup | Sign up at baserow.io; no installation, no servers, no technical setup | `docker run -v baserow_data:/baserow/data -p 80:80 -p 443:443 baserow/baserow` — a single-container deploy, but still requires a server and basic Docker familiarity |
| Backups, updates, monitoring | Fully managed by Baserow | Your responsibility |
| Air-gapping | Not possible — this is a hosted SaaS | Fully supported — can run with no internet access at all, relevant for high-sensitivity deployments (government, medical, financial data cited as examples in Baserow's own documentation) |
| Row/storage limits | Free tier capped at 3,000 rows / 2GB per workspace; higher tiers raise this | No platform-imposed limit — bounded only by your own server's resources |

## Data access

| | Baserow Cloud | Self-hosted Baserow |
|---|---|---|
| Direct database access | Not permitted, for security reasons — REST API only | Full access to the underlying PostgreSQL database; raw SQL queries are possible directly against it |
| Third-party processor relationship | Yes — see `platform-needs-assessment.md`, Table 2, for the current state of DPA/TOM/SCC verification | No — data never leaves infrastructure you control, closing the third-party-processor gap flagged throughout Table 2 and `data-privacy.md` |

## Licensing and cost

- The **core self-hosted version is free and open-source** (MIT), with unlimited usage of all non-premium, non-enterprise features.
- A paid licence is only needed self-hosted to unlock advanced enterprise features — role-based access control (RBAC) and certain integrations are named examples.
- Baserow Cloud's paid tiers (Premium, Advanced) unlock features like Kanban/Calendar/Survey views and higher row/storage limits, separate from the self-hosted licensing question.

## AI features

Relevant given this project's existing preference for local, on-device AI (see `self-hosted-architecture/architecture-self-hosted-technical.md`): self-hosted Baserow can connect directly to a configured AI provider at the workspace or instance level, **including local Ollama**, for offline or air-gapped setups. Baserow Cloud instead uses Baserow's own managed AI connection path. This mirrors the same local-vs-cloud AI split already made for the CRM's own architecture, applied to Baserow's platform-level AI features too.

## What this means for this project

RCM Cooperative's own CRM currently runs on **Baserow Cloud**, and the practical findings in `training.md` (the export/import mechanism, the duplicate-detection automation, the Edit row link field) were all built and confirmed against Cloud specifically.

**Self-hosted Baserow is worth considering for a deployment where:**
- The third-party-processor relationship in Table 2 is a genuine blocker (for example, an institution's own governance won't accept it)
- Dedicated IT infrastructure is already available — the same condition that makes the fully custom self-hosted SQL design viable (see `self-hosted-architecture/README.md`)
- Air-gapping or direct SQL access is a real requirement

<mark>Not yet confirmed: whether the specific automations built for this project (the "Self-link on name match" duplicate-detection workflow, see `training.md`) work identically on self-hosted Baserow, or whether Automations is a Cloud-only or higher-tier-only feature when self-hosting. Worth testing directly before assuming parity, given how much of this project's build depends on that automation working as designed.</mark>
