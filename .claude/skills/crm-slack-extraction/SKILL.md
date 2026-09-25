---
name: crm-slack-extraction
description: Extract People/Interactions entries for RCM Cooperative's Baserow CRM from a Slack Standard Export (public channels only), producing an import-ready xlsx with uncertain fields flagged. Use this whenever Cass asks to "extract Slack activity for the CRM", "run the Slack extraction", or hands over a Slack export folder. Self-contained — does not depend on crm-notes-extraction's files (see "On duplication" below). Lives under .claude/skills/ purely as a matter of where scripts are collected in this repo — it does NOT use an LLM in its current form. The entire pipeline is one deterministic Python command (scripts/run_pipeline.py); no Claude Code session, local or hosted, is needed to run it (see "Parked features" for what would reintroduce one).
---

# CRM Slack Extraction

Turns one Slack Standard Export (public channels only, per RCM Cooperative's current Free-tier plan) into new/updated People and Interactions rows for the Baserow CRM, output as an xlsx ready for manual import.

**This is a code pipeline, not an LLM skill, despite living under `.claude/skills/`.** It's filed here only because that's where Cass is collecting this repo's scripts — invoking it does not require Claude Code, `claude-local`, or `claude-cloud` at all. Running it is one command:

```
python3 .claude/skills/crm-slack-extraction/scripts/run_pipeline.py --date <yyyymmdd>
```

That's normally the whole command — every path (export folder, channel-mapping CSV, people-export CSV, every output file) is derived from `<yyyymmdd>` automatically, matching the `private/slack/slack-export-<yyyymmdd>/` convention. Override any individual path with `--export-dir`, `--channel-mapping`, or `--people-export` only for a non-standard layout.

If `--date` is omitted, the script prompts for it interactively — an ISO `YYYYMMDD` date, e.g. `20260907`, rejecting anything else.

**Current scope also builds a candidate People list.** Every unique Slack user found across all mapped channels (deleted/bot accounts excluded) is written as a new People-table row — see "Known limitation: no existing-CRM dedup" below.

This only records **channel membership** as `people-participants` and the **channel's active date range** (derived from message-file names only, never their content) as `date-started`/`date-last-activity`. It does not analyse individual activity levels, and it does not read or summarise message content. See "Parked features" below for what was deliberately left out and why.

## Known limitation: no existing-CRM dedup

The People-table candidate list is built purely from the Slack export — it makes **no attempt to check whether a person already exists** in the live Baserow People table. Every unique, non-deleted, non-bot Slack user found in a mapped channel becomes a candidate row, including people who are already in the CRM under a different or the same email. This is a deliberate simplification for the current deployment, not an oversight: checking properly would need either a full, freshly-exported People table cross-referenced by email (still fragile — stale the moment someone new is added after the export), or a live Baserow API query per candidate (not implemented here). Cass reviews the generated People sheet by eye before adding anything to Baserow. **A live API-based existence check is a reasonable future development** if this skill's usage grows to a scale where manual review of the full candidate list becomes impractical — not built now.

**On duplication — read this before assuming something's out of sync by accident.** This skill deliberately holds its own copies of `references/schema.md` and `scripts/build_workbook.py`, identical in content to the ones in `.claude/skills/crm-notes-extraction/`, so this skill can be run (or handed to someone else) in isolation without needing the notes-extraction skill present at all. This is the same kind of manually-kept-in-agreement tradeoff already known from this skill's earlier (now-dropped) attempt to track Baserow's exact on-screen column order — see `schema.md` and `scripts/build_workbook.py`'s module docstring — extended here to the whole schema file and build script. **If the live Baserow schema changes, both skills' copies of `schema.md` and `build_workbook.py` need updating together.** A planned later refactor is to pull both into a shared `references/` location both skills point to instead of duplicating — not done yet; don't do it unprompted, Cass will direct that packaging work when it happens.

**Column order in the output xlsx no longer matches Baserow's on-screen order — read the warning.** `build_workbook.py` used to try to reproduce Baserow's live column order exactly (via manual screenshots), so a row range could be pasted straight across without realigning. That's been dropped — see `references/schema.md`'s "Column order — deliberately NOT tracked" section, and the warning sheet the pipeline now adds to every output workbook — because it wasn't a robust way to track drift and it constrained anyone templating their own Baserow instance from RCM's. Every generated workbook now opens on a "READ FIRST" sheet telling the reviewer to match columns by header name, not position, before pasting. Baserow's own Import feature (header-name matching) is the natural fix for this and is noted as a future development opportunity — not implemented in this skill yet.

**Scope note**: this version only handles Standard Export data (public channels). Private-channel export (via a user-token app) is a deliberately deferred later phase — do not attempt to read private-channel data with this skill unless Cass has explicitly extended its scope.

**Path convention** — every path below is written in full from the repo root. Do not shorten or reconstruct a "relative to this skill" version.

## Parked features — potential future development

Two pieces of analysis were designed, then deliberately parked before implementation, and are **not** part of this skill's current scope:

- **Lead-status signals** — per-user activity counts (message frequency, threads started, reactions received) as a basis for flagging someone as a channel "lead," beyond bare membership.
- **Discussion-summary notes** — an LLM reading a channel's message text to write a factual summary for the Interaction's `notes` field.

Both are parked for the same reason: they involve analysing individual community members' activity or message content, and that isn't something to decide unilaterally ahead of a conversation with the community about the use of LLMs (and, for lead-signals specifically, behavioural analysis generally) on their data. This is independent of the fact that lead-signals itself doesn't require an LLM to compute — it was parked alongside the summary step on the same ethical grounds, not for technical reasons.

**Both remain worth revisiting later**, once that community conversation has happened — noted here as a development opportunity, not a closed door. If reinstated, `references/local-llm-setup.md` documents how to wire up a local Qwen model for the summary step specifically (a single scoped completion call, not full agentic orchestration — see that file's notes on why). Do not reintroduce either without an explicit instruction from Cass.

## Step 0: Confirm every file exists

Check these exact paths before doing anything else; stop and report the exact missing path if any aren't found — do not guess an alternative location:

- `.claude/skills/crm-slack-extraction/references/schema.md`
- `.claude/skills/crm-slack-extraction/references/slack-export-format.md`
- `.claude/skills/crm-slack-extraction/scripts/build_workbook.py`
- `.claude/skills/crm-slack-extraction/scripts/parse_slack_export.py`
- `.claude/skills/crm-slack-extraction/scripts/run_pipeline.py`
- The Slack export folder, `private/slack/slack-export-<yyyymmdd>/`, containing `users.json`, `channels.json`, and per-channel message folders
- `private/slack/slack-export-<yyyymmdd>/channel-mapping-<yyyymmdd>.csv` — lives inside the export folder itself, not at `private/` top level (see Step 1 — if this doesn't exist yet, `run_pipeline.py` generates a starter version automatically and stops for review; see `references/how-to-run.md`'s "First run" section)

## Step 1: Channel-to-entity mapping (the only manual input)

`private/slack/slack-export-<yyyymmdd>/channel-mapping-<yyyymmdd>.csv` is Cass-maintained, not generated by this pipeline, and is the one genuine judgement call in the whole thing. It lives inside the export folder itself, alongside `users.json`/`channels.json` — keeping each date's inputs and outputs together in one place, since this is also where `run_pipeline.py` writes its outputs (see Step 2). Two columns: `channel`, `mapping` — either an existing Interaction's name (Slack activity folds into that Interaction's `notes`, no new row) or the literal value `standalone` (its own `slack-channel` Interaction row, named after the channel).

If a channel in the export isn't in this file, the pipeline stops and lists it — it will not guess which case it is. This is the hardest judgement call in the pipeline and is deliberately kept manual. On a first run for a given export date, if the file doesn't exist at all, `run_pipeline.py` generates a starter version itself — one row per channel, `mapping` pre-filled as `standalone` — then stops without proceeding further, so nothing is written to the CRM from an unreviewed guess. Given this skill's public-channels-only scope, `standalone` is genuinely correct for most channels (open topic/community spaces); see `references/how-to-run.md`'s "First run" section for the narrower set of cases where a channel should instead map to an existing Interaction's name.

## Step 2: Run the pipeline

```
python3 .claude/skills/crm-slack-extraction/scripts/run_pipeline.py --date <yyyymmdd>
```

One command, pure computation, no LLM. `<yyyymmdd>` is the Slack export's date (ISO `YYYYMMDD`, e.g. `20260907`) — prompted for interactively if `--date` is omitted, and validated as exactly 8 digits before anything else runs. `<yyyymmdd>` is normally the only thing you need to supply; it:
- Derives the export directory as `private/slack/slack-export-<yyyymmdd>/` (override with `--export-dir` for a non-standard layout).
- Derives the channel-mapping path as `private/slack/slack-export-<yyyymmdd>/channel-mapping-<yyyymmdd>.csv` (override with `--channel-mapping`).
- Derives the People-export path as `private/slack/slack-export-<yyyymmdd>/people-export.csv`, used automatically if it exists (override with `--people-export`, or simply don't create that file if you don't want matching for this run).
- Loads `users.json`, filtering out `deleted` and `is_bot` accounts.
- Builds a **People-table candidate row for every unique Slack user found across every mapped channel** (both standalone and existing-Interaction ones), deduplicated by Slack user ID, with `name-person-first`/`name-person-last` split from the Slack real name and `email-1` where available. Written to `candidates-<yyyymmdd>.csv` ahead of the Interactions rows. No dedup against the live CRM is attempted — see "Known limitation" above.
- For each mapped channel, reads `channels.json`'s `members` list — this becomes `people-participants` (membership = participant, per Cass's decision — no minimum-activity floor, and no per-user activity analysis at all currently — see "Parked features").
- Reads the *names* of each channel's per-day message files (`YYYY-MM-DD.json`) to determine `date-started` and `date-last-activity` — it never opens or reads the content of these files.
- If a People-export CSV is found or given (with `name-person`/`email-1`/`email-2` columns — see `references/schema.md`), matches each member's Slack email against it, using the matched canonical name where found. Without one, every member is written under their Slack display name and flagged as unmatched.
- Writes `candidates-<yyyymmdd>.csv` (inside the export folder, alongside the mapping CSV — see "Path convention" above): a complete Interactions row (`type`, `name-interaction-long`, `people-participants`, `date-started`, `date-last-activity`) for every **standalone** channel. Channels mapping to an existing Interaction are printed in the run summary instead, for Cass to update that Interaction's `notes` by hand — the pipeline has no access to the live Baserow row.
- Writes `flagged-unmatched-users-<yyyymmdd>.csv` (same folder) if any member couldn't be matched.
- Runs `build_workbook.py` itself as its final step, producing `crm-extraction-output-<yyyymmdd>.xlsx` (same folder).
- Adds one extra worksheet per standalone channel to that xlsx, named after the channel: a plain single-column list of that channel's participants, alphabetical — for easy copy/paste into Baserow, as an alternative to reading names out of the `people-participants` cell on the main Interactions sheet.

`notes` and `people-leads` are intentionally left blank throughout (see "Parked features") — the pipeline never populates either field.

If the mapping CSV and the export don't line up (a channel missing from one or the other), the pipeline stops with the exact mismatch named — it does not proceed past an unresolved mismatch, and does not run `build_workbook.py` in that case.

## Output format

The xlsx, a row-count summary printed by `build_workbook.py`, plus `flagged-unmatched-users-<yyyymmdd>.csv` if applicable and the unresolved-channel-mapping list if any channel wasn't fully resolved before the run. All output files land in the same export folder as the mapping CSV (see "Path convention" above).

## When to flag instead of deciding

- A channel not yet in `channel-mapping-<yyyymmdd>.csv` — the pipeline stops rather than guessing.
- A Slack user who can't be matched to an existing People row via email — written to `flagged-unmatched-users-<yyyymmdd>.csv`, still included as a participant under their Slack name, never silently dropped or silently created as a new person.
- Anything requiring information not present in `users.json`/`channels.json`/filenames/the people export (no web search, no guessing, and — per "Parked features" — no reading of message content).
