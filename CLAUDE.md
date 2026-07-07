# CLAUDE.md — RCM CRM Project Context

## Working preferences (apply throughout this project)
- UK English spelling throughout.
- Brief, balanced responses — avoid large blocks of text, no sycophantic or superfluous language.
- Hold/go protocol: when given multiple pieces of information or files across turns, wait for explicit "go" before acting.
Don't process partial input.
- Default working format is markdown.
Pandoc is used to convert markdown to PDF for reports/dissemination.
- Prefer generalisable, reusable structures over one-off solutions.
Documentation is a deliberate, valued part of the process, not an afterthought.
- Prefer open-source over proprietary/big-tech tools.
Privacy-conscious, GDPR-aware — this project involves research community data and must be designed accordingly.
- Prefer robust, well-architected solutions over quick manual workarounds (e.g. separate config profiles/aliases rather than editing a shared settings file each time).
- In documentation and markdown, start each new sentence on a separate line (semantic line breaks).
This makes diffs easier to read in version control.

## Project overview
A self-hosted, open-source CRM for Research Community Managers (RCMs), built by the RCM Cooperative.
Designed from the outset to be cloned and handed off to individual client communities as well as used for the cooperative's own community.

Evolves from a prior MVP: github.com/rcmcooperative/community-mapping (SharePoint Lists → Python conversion → Kumu visualisation).
This project replaces the SharePoint layer while keeping Kumu as the public-facing visualisation layer.

## Resolved architecture decisions

1. **Hosting**: self-hosted, intermittent uptime acceptable.
No requirement for the CRM to be always-on or publicly reachable in v1.
2. **Canonical ID**: ORCID identified as the long-term canonical identifier concept, but ORCID OAuth integration is deferred to v2.
v1 has no self-service beyond a simple point-of-entry consent-confirmation form (no token auth, no OAuth).
3. **Consent**: captured once, at point of entry only, for v1.
No ongoing self-service correction/withdrawal flow yet — handled manually if needed.
(A token-based, ORCID-authenticated self-service correction form is designed conceptually for v2, informed by ethical considerations from an unsuccessful Astera grant application — see decision log.)
4. **Database**: SQLite for v1.
Document a clear migration path to Postgres for later versions if concurrent multi-user editing becomes necessary.
5. **Sync model**: pull-based only (not webhooks/push) for all external integrations (Slack, GitHub, Zenodo) — consistent with intermittent-uptime hosting.
6. **Schema philosophy**: generic relationship model and generic custom-field model (not fixed dedicated tables/columns per relationship or field type).
Goal: avoid typical CRM bloat/noise; let RCMs add, hide, or remove fields and relationship types without code changes or migrations.

## Data model (entities)
- Contacts (people)
- Organisations
- Projects
- Relationships (generic: entity_a_type/id, entity_b_type/id, relationship_type)
- Custom_Fields (generic: entity_type/id, field_name, field_value, visible flag)
- Interactions / Engagement_Activities
- MOE stage history (audit trail, not just current value)
- Consent records
- Pending-review table (for any future submitted corrections — not live in v1)
- Communications log

## Feature set (v1 scope)
- MOE (Mountain of Engagement) stage tracking with full stage-history audit trail
- Automated stage-progression suggestions (RCM confirms, not auto-applied)
- Mountain-shaped visualisation (scaled parallelograms per stage) + kanban board view
- Stalled/at-risk flagging (no recent interaction).
CRM surfaces this fact only; interpretation/strategy is a human decision, not CRM logic.
- Tagging/segmentation, potentially with local-Qwen-suggested tags based on interaction content
- Duplicate-contact detection across multi-source intake
- Communication log (outreach sent, separate from interactions received)
- Reporting via version-controlled Jupyter notebooks: read-only DB connection, pseudonymised IDs only (no identifying fields in reports), separate authenticated lookup step to resolve ID → identity.
Reports are local-only in v1 (no auto-publish; Zenodo publishing path is a future option).

## Explicitly deferred (v1.1+ / v2)
- ORCID OAuth / self-service correction form (token-based, designed conceptually, not built)
- Email marketing/comms tooling (future integration candidates: Mailchimp, "Yet Another Mail Merge")
- NLP/chatbot-based contact entry
- Photo/name-tag OCR entry (would need a vision-capable local model)
- Federated cross-community data exchange (from an unsuccessful Astera Open Science Fellowship application) — design should leave room for this without building it now

## Multi-client design intent
Architecture is deliberately built for handoff: single template repo cloned per client, client-specific field/relationship specifications layered on top per deployment, then the finished Docker setup handed to the client to self-host going forward.
This was an intentional design goal from the start, not incidental.

## Email integration (related, separate system)
A local pipeline (Gmail API + Qwen3 via Ollama, fully local) matches senders to CRM contacts and creates Engagement_Activities from matched threads.
Unmatched senders become candidate-contact issues in a private "CRM-onboarding" GitHub repo (permanent audit log).
A separate "follow-up tracker" repo flags stale sent threads (disposable, pruned periodically).
Both repos' open issues should surface inside the CRM via (a) a global open-issues count/summary and (b) per-contact flags — not just visible in GitHub directly.

## Local AI
Qwen3 via Ollama, run natively on the host machine — not containerised.
On Apple Silicon, Docker cannot pass through GPU acceleration, so Ollama must stay outside the container.
The CRM container should reach it via `http://host.docker.internal:11434`, not `localhost`.

## Local vs cloud model switching
Two fully separate Claude Code config profiles, so cloud and local never fight over the same settings file:

- **Cloud (default)**: `~/.claude/settings.json` — clean, no env overrides, `"model": "claude-sonnet-4-6"`.
- **Local**: `~/.claude-local/settings.json` — contains the Ollama routing:
```json
  {
    "env": {
      "ANTHROPIC_AUTH_TOKEN": "ollama",
      "ANTHROPIC_BASE_URL": "http://localhost:11434",
      "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
    },
    "model": "qwen-coder-local",
    "theme": "dark"
  }
```

**Aliases** (in `~/.zshrc`):
```bash
alias claude-cloud='claude --model claude-sonnet-4-6'
alias claude-local='CLAUDE_CONFIG_DIR=~/.claude-local claude'
```

Before starting work, check the active model/profile with `/status` inside the session.
Don't assume based on which alias you think you ran.

**Known gotcha**: an active conda environment can inject `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` via its activation scripts, silently routing a cloud session to local Ollama even with clean settings.json and no manually-set env vars.
If `/status` shows an unexpected base URL, run `conda deactivate` and check again before assuming a settings.json problem.

## Documentation & review process
Design/scope documentation and open questions live in this separate repo (rcm-crm), distinct from the operational repos (CRM-onboarding, follow-up tracker).
Repo is private initially for review by a DataLad-affiliated developer friend, via GitHub issues used as a decision log.
Will be opened publicly after that review.

## Ethical considerations (carried from Astera application ethics analysis)
- Consent and individual review rights are central.
People should be able to see and verify what's recorded about them (deferred to v2 for active self-service, but the principle should shape the schema now, e.g. consent flag per person).
- Avoid surveillance/chilling effects.
Be transparent and proportionate about what's tracked and why.
- Watch for bias in engagement scoring.
Raw activity counts can systematically under-represent less-resourced or non-English-fluent contributors; MOE rubric weighting should be documented and justified, not treated as neutral.
- Data minimisation — collect only what serves a stated, communicated purpose.
- Keep scoring/analysis logic inspectable, not a black box.