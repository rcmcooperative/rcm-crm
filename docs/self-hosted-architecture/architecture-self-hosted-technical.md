# RCM CRM — Technical Architecture

This document describes the technical design of the RCM-CRM in detail.
For the conceptual/ethical rationale behind this design, see `../why-crm.md` and `../engagement-framework.md`.
For a plain-language architecture summary, see `architecture-self-hosted-lay-summary.md`.
For why this document describes one deployment option rather than the CRM's current live architecture, see `README.md`.

## Hosting model

Self-hosted, with intermittent uptime accepted by design.
The CRM is not required to be always-on or publicly reachable in v1.
This keeps the technical bar for running an instance low enough that an individual RCM can run it on their own machine, without needing a VPS, cloud account, or dedicated always-on hardware.

## Database

SQLite for v1.
SQLite comfortably handles the expected data volume (in the low thousands of contacts, with a larger volume of interaction records) for a single-maintainer or small-team deployment.
A migration path to Postgres is documented for later versions, should a deployment need concurrent multi-user editing at scale.

## Data model

### Core entities
- **Contacts** — people
- **Organisations**
- **Projects**

### Generic, extensible structures
Rather than fixed dedicated tables or columns per relationship or field type, the schema uses two generic structures:

- **Relationships** — `entity_a_type`, `entity_a_id`, `entity_b_type`, `entity_b_id`, `relationship_type`. Adding a new relationship type (for example, Project → Funder) requires no schema change or migration — just a new `relationship_type` value.
- **Custom_Fields** — `entity_type`, `entity_id`, `field_name`, `field_value`, `visible` flag. Adding, hiding, or removing a field is a data operation, not a code change. The `visible` flag allows a field to be hidden without deleting its historical data.

This design deliberately avoids the bloat and noise common to off-the-shelf CRMs, where many fields go unused but remain visible.
It also lets individual RCM Cooperative client deployments diverge in which fields and relationships they track, without diverging in the underlying codebase.

### Engagement-specific structures
- **Interactions / Engagement_Activities** — records of activity linked to a contact, tagged by source and type
- **MOE stage history** — a full audit trail of stage changes over time, not just the current value (see `../engagement-framework.md` for the stage definitions)
- **Consent records**
- **Pending-review table** — reserved for future submitted corrections (not active in v1)
- **Communications log** — outreach sent, distinct from interactions received

## Canonical identity

ORCID is the long-term canonical identifier concept for contacts.
ORCID OAuth integration is deferred to v2.
In v1, there is no self-service identity verification beyond a simple point-of-entry consent-confirmation form.

## Consent model

Consent is captured once, at point of entry, for v1.
There is no ongoing self-service correction or withdrawal flow yet in v1; this is handled manually if needed.

A token-based, ORCID-authenticated self-service correction form is designed conceptually for v2, informed by the ethical considerations documented from an unsuccessful Astera Open Science Fellowship application (see decision log).

Where a project uses two-tier visibility, `internal_visible` defaults to true (legitimate interest basis) and governs internal-only views; `external_consent` defaults to null until explicitly granted, and governs any public-facing output (for example, a public Kumu view). Consent does not block contact creation, only public visibility.

## Sync model

Pull-based only, not webhooks or push, for all external integrations (Slack, GitHub, Zenodo).
This is consistent with the intermittent-uptime hosting model: a pull-based job can run whenever the machine happens to be on, without requiring the CRM to be reachable from outside at any specific moment.

## Email integration

A local pipeline (Gmail API + a local LLM run via Ollama, fully on-device) matches senders to CRM contacts and creates Engagement_Activities from matched threads, using a generated summary rather than the raw email body.

Unmatched senders become candidate-contact issues in a private "CRM-onboarding" GitHub repository, which also serves as a permanent audit log once issues are reviewed and closed.
A separate "follow-up tracker" repository flags stale, unanswered sent threads; unlike the onboarding log, these issues are disposable and pruned periodically.

Both repositories' open issues surface inside the CRM itself, via a global open-issue count/summary and per-contact flags, rather than requiring a separate check in GitHub.

Scheduling runs via a local watchdog job that checks whether a scheduled run was missed (for example, because the machine was asleep) and fires a catch-up run and notification if so.

## Local AI

Any local model inference (for example, engagement-activity summarisation, or tag suggestions) runs natively on the host machine via Ollama, not inside a container.
On Apple Silicon, Docker cannot pass GPU acceleration through to a containerised process, so this separation is a performance necessity, not just a convenience.
A containerised CRM reaches the host's local model via `http://host.docker.internal:11434`, not `localhost`.

## MOE tracking and engagement scoring

Full detail is in `../engagement-framework.md`.
In brief: the CRM stores a full stage-history audit trail (not just current stage), supports automated stage-progression suggestions that require RCM confirmation rather than auto-applying, and provides both a mountain-shaped visualisation and a kanban board view of contacts by stage.

Stalled/at-risk flagging (no recent interaction) is descriptive only.
The CRM surfaces the fact; interpreting why, and deciding what to do about it, is a human strategic decision, not something the CRM infers or acts on.

## Duplicate detection and tagging

Duplicate-contact detection runs across multi-source intake (the same person appearing via Slack, a sign-up form, and email, for example).
Tagging and segmentation are supported as free-form, extensible data (via Custom_Fields), with the possibility of local-model-suggested tags based on interaction content — always surfaced as a suggestion for human confirmation, not applied automatically.

## Reporting

Reporting runs via version-controlled Jupyter notebooks, connecting to the database in read-only mode.
Reports use pseudonymised IDs only; no identifying fields appear in report output.
Resolving a pseudonymous ID back to an identifiable contact requires a separate, authenticated lookup step, not something embedded in the report itself.

Reports are local-only in v1; a future Zenodo publishing path is a possible v2 addition.
Generated report output (containing real, if pseudonymised, data) is kept in a gitignored local folder, never committed to version control.

## Multi-client design

The architecture is deliberately built for handoff: a single template repository is cloned per client, client-specific field and relationship specifications are layered on top per deployment, and the finished Docker setup is handed to the client to self-host going forward.
This was an intentional design goal from the outset, reflecting a preference for reproducible, generalisable structures over one-off solutions.

## Explicitly deferred to v1.1 or later

- ORCID OAuth and the associated self-service correction form
- Email marketing/comms tooling integration (for example, Mailchimp or Yet Another Mail Merge)
- Natural-language or chatbot-based contact entry
- Photo/name-tag OCR entry
- Federated cross-community data exchange, as explored in the unsuccessful Astera Open Science Fellowship application — the design leaves room for this without building it now
