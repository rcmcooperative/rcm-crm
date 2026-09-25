# CLAUDE.md — RCM-CRM Project Context

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
- Prefer robust, well-architected solutions over quick manual workarounds.
- In documentation and markdown, start each new sentence on a separate line (semantic line breaks).
This makes diffs easier to read in version control.

## Project overview
A CRM for Research Community Managers (RCMs), built by the RCM Cooperative.
**Current live architecture is Baserow-based**, not the original self-hosted SQL design — see `docs/README.md` for the full documentation index.
Designed from the outset to be cloned and handed off to individual client communities as well as used for the cooperative's own community, via Baserow's workspace export/import mechanism (see `docs/baserow/training.md`).

Evolves from a prior MVP: github.com/rcmcooperative/community-mapping (SharePoint Lists → Python conversion → Kumu visualisation).
Kumu remains the public-facing visualisation layer; the intake/database layer has moved twice — SharePoint → SeaTable (rejected mid-build) → Baserow (current).

## Current architecture (Baserow)

Five tables: People, Organisations, Communities, Interactions, Projects — a full relationship mesh, several table pairs linked by more than one distinct role (e.g. People↔Projects via leads/contributors/contact separately).
Full schema, field reference, and relationship diagram: `docs/baserow/schema.md`.
System overview (data sources → Web App → Database → self-serve → outputs): `docs/baserow/architecture-overview.md`.

**Platform choice**: Baserow was chosen over SharePoint Lists, SeaTable, and the original self-hosted SQL design — see `docs/platform-needs-assessment.md` for the full comparison and rationale.
Baserow Cloud vs. self-hosted Baserow: `docs/baserow/self-hosted-vs-cloud.md`.

**Practical findings from building this** (keyboard shortcuts, the duplicate-detection automation, export/import mechanics, formula gotchas): `docs/baserow/training.md`.

## Self-hosted SQL design — an alternative, not the current build

The original v1 design (self-hosted, SQLite/Postgres, generic Relationship/Custom_Fields schema, Docker-based multi-client handoff) is preserved in `docs/self-hosted-architecture/`, since it remains the right choice for deployments needing full data-privacy control and where dedicated IT infrastructure is available.
It is **not** what RCM Cooperative's own CRM currently runs on.
See `docs/self-hosted-architecture/README.md` for when to use this over the Baserow build.

## Data ingest and export skills (built as Claude Code skills, not part of the CRM's own runtime)

- **crm-notes-extraction** — parses meeting notes into People/Organisations/Communities/Projects/Interactions rows. **Uses an LLM** (primarily `claude-cloud`; local Qwen models proved unreliable at the structured hand-off format needed here, after extensive testing). One notes file = one Interaction, regardless of how many dated sections it contains. Output matches Baserow's real on-screen column order (captured via screenshot, not the field-definitions API's unreliable `order` property).
- **crm-email-contacts** — **deterministic code only, no LLM call at all** (deliberately — the privacy concern is about exposing CRM data to a model's reasoning, not about code reading it). Matches Google Contacts exports against existing People records by name, fills in emails and a derived `org_domain`, flags new/uncertain entries for review.
- **crm-slack-extraction** — **deterministic code only, no LLM call**. Built, matching the pattern above: public-channels-only Standard Export (RCM Cooperative's Slack workspace is on the Free tier; private-channel export deferred). Produces People candidates from channel membership and Interactions rows for standalone channels, plus a flagged-unmatched-users CSV. No existing-CRM dedup in this skill — relies on Baserow's own duplicate-detection.
- **crm-kumu-visualisation** — **deterministic code only, no LLM call**. Converts the five Baserow exports into Kumu-ready `elements`/`connections` workbooks. Interactions are not Kumu nodes — flattened into pipe-separated metadata on the other four node types. Produces two exports: `kumu-import-internal` (full data, real names) and `kumu-import-public` (consent-filtered via `mapping-consent` — people without active public consent are excluded entirely, pseudonymised people get a stable SHA-256-hashed label). Edge types are generic (lead, participant, contact, contributor, employee, sponsor, funder, child-of, affiliated) for now. See `docs/baserow/schema.md` for the full edge/consent registry this pipeline implements, and note two flagged open questions there (the `affiliated` edge type, and confirming the exclude-vs-pseudonymise consent policy).
- **populate-repo-template** — **uses an LLM** (fills in this template's README/CONTRIBUTING/CoC placeholders from project context; not a deterministic transform).

## Multi-client design intent

Architecture is deliberately built for handoff: a single Baserow workspace template (`rcm-crm`), structure-only exported and shared, imported by each client into their own Baserow account (Free tier confirmed sufficient — see `docs/baserow/training.md`).
This was an intentional design goal from the start, not incidental, and predates the platform's move from SharePoint to SeaTable to Baserow.

## Local vs cloud model switching (for this project's own development work in Claude Code)

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

**Known gotchas:**
- An active conda environment can inject `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` via its activation scripts, silently routing a cloud session to local Ollama even with clean settings.json and no manually-set env vars.
If `/status` shows an unexpected base URL, run `conda deactivate` and check again before assuming a settings.json problem.
- This local/cloud split is unrelated to the CRM's own AI features. The CRM's data-ingest skills each have their own, separate AI-usage decisions (see above) — some use claude-cloud, some use no LLM at all.

## Documentation & review process

Design/scope documentation lives in `docs/` in this repo (see `docs/README.md` for the index), distinct from the operational repos (CRM-onboarding, follow-up tracker).
Repo is private initially for review by a DataLad-affiliated developer friend, via GitHub issues used as a decision log.
Will be opened publicly after that review.

## Ethical considerations (carried from Astera application ethics analysis; architecture-agnostic)
- Consent and individual review rights are central.
People should be able to see and verify what's recorded about them.
- Avoid surveillance/chilling effects.
Be transparent and proportionate about what's tracked and why.
- Watch for bias in engagement scoring.
Raw activity counts can systematically under-represent less-resourced or non-English-fluent contributors; MOE rubric weighting should be documented and justified, not treated as neutral.
- Data minimisation — collect only what serves a stated, communicated purpose.
- Keep scoring/analysis logic inspectable, not a black box.

Full detail: `docs/why-crm.md`, `docs/data-privacy.md`, `docs/engagement-framework.md` (currently marked NEEDS REVIEWING — check before treating as current).
