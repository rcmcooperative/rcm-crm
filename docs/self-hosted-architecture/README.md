# Self-hosted SQL architecture

This folder describes the original RCM-CRM design: a self-hosted, Docker-based application connecting to a local SQLite or Postgres database.

**This is not the architecture the RCM Cooperative's own CRM currently runs on.** The live system is built on Baserow — see `../baserow/architecture-overview.md` and `../baserow/schema.md` for the current design.

This design remains genuinely relevant for two reasons:

1. **It scores highest on data privacy and control** of every option compared in `../platform-needs-assessment.md` — no third-party processor is involved at all. It's the right choice for a deployment with dedicated institutional IT support, and where that level of infrastructure burden is acceptable.
2. **The generic, extensible data model** (relationships and custom fields as data, not schema) described here shaped the design philosophy carried into the Baserow build too, even though the underlying mechanism is different.

## A note on self-hosting going forward

Baserow itself is open source and self-hostable (see `../platform-needs-assessment.md`, Table 1). For a deployment that wants self-hosting's privacy properties without building this custom SQLite/Postgres application from scratch, **self-hosting Baserow itself** may be the simpler path — see `../baserow/self-hosted-vs-cloud.md`. This custom architecture remains the right choice where Baserow's own data model or feature set doesn't fit the deployment's needs, not the default self-hosting route by default.
