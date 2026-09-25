# How to Run This Skill

**This does not use an LLM.** It lives under `.claude/skills/crm-slack-extraction/` purely because that's where this repo collects its scripts — not because it needs Claude Code, `claude-local`, or `claude-cloud` to run. With lead-status signals and discussion-summary notes parked (see `SKILL.md`'s "Parked features"), the entire pipeline is deterministic Python. You never need to open a Claude session to run it.

This skill is fully self-contained — everything it needs lives under `.claude/skills/crm-slack-extraction/`. It does not require `crm-notes-extraction` or any other skill to be present.

## Path convention

Everything for one export date lives together, inside that export's own folder:

```
private/slack/slack-export-<yyyymmdd>/
├── users.json                          (from the Slack export itself)
├── channels.json                       (from the Slack export itself)
├── <channel-name>/...                  (from the Slack export itself)
├── channel-mapping-<yyyymmdd>.csv      (yours — see step 1)
├── people-export.csv                   (yours, optional — see step 2)
├── candidates-<yyyymmdd>.csv           (written by run_pipeline.py)
├── flagged-unmatched-users-<yyyymmdd>.csv   (written, if needed)
└── crm-extraction-output-<yyyymmdd>.xlsx    (written — the final workbook)
```

Keeping the mapping file and people-export alongside the raw export data — rather than at `private/`'s top level — means every output the pipeline produces also lands in that same folder (it writes wherever the mapping CSV lives), so a whole export date's inputs and outputs stay together as one unit.

## 1. Prepare the Slack export and (usually) the channel-mapping CSV

- **The Slack export**, unzipped at `private/slack/slack-export-<yyyymmdd>/`, containing `users.json`, `channels.json`, and one folder per public channel — where `<yyyymmdd>` is the export's date in ISO form (e.g. `20260907`). See `references/slack-export-format.md` for what's in each file.
- **`private/slack/slack-export-<yyyymmdd>/channel-mapping-<yyyymmdd>.csv`** — two columns, `channel,mapping`. Every channel present in the export needs a row here: either the name of an existing Interaction (this channel's activity folds into that Interaction's notes) or the literal value `standalone` (gets its own `slack-channel` Interaction row). This is the one genuinely manual, judgement-based input — the pipeline will not guess it. You don't need to create this file by hand, though — see "First run" below.

### First run: creating the channel-mapping CSV

If this file doesn't exist yet for this export date, `run_pipeline.py` creates a starter one for you automatically — you don't need to create it by hand, just run the command in step 3 below. It fills in one row per channel found in `channels.json`, with `mapping` pre-filled as `standalone` for every channel — then it stops, so nothing is written to the CRM from an unreviewed mapping. You'll see something like:

```
No channel-mapping CSV found — created a starter one at private/slack/slack-export-<yyyymmdd>/channel-mapping-<yyyymmdd>.csv
  4 channel(s) listed, all pre-filled as 'standalone'.
  Review it: change any channel that's really the Slack side of an existing Interaction to that Interaction's exact name instead of 'standalone' — see references/how-to-run.md's "First run" section for when that applies.
  Then re-run this same command.
```

Open the generated file, review each row, and re-run the same command once you're satisfied. Since this export type only covers **public** channels, `standalone` will genuinely be correct for most rows — public channels tend to be open topic/community spaces (`funding-opportunities`, `general`) rather than the Slack side of one specific tracked relationship. The cases worth changing to an existing Interaction's name instead are narrower than they might first seem:

- **The channel exists specifically to coordinate with one already-tracked relationship** — e.g. a channel created for one named Project or one specific partner organisation, where meetings for that same relationship already have their own Interaction row. Slack chatter there is just another channel of the *same* relationship, not a separate thing — folding it in avoids two rows (a meeting Interaction and a separate Slack-only Interaction) representing what's really one ongoing relationship.
- **The channel is a temporary, single-purpose scratch space for one specific event or meeting** that already has (or will have) its own Interaction from meeting notes — e.g. logistics coordination for one summit or one workshop. The channel is standing in for that one interaction, not an ongoing thing in its own right.
- **The channel is the Slack-side companion to a Community or Project that already has an established recurring-Interaction convention** (e.g. a monthly call), where the intent is for Slack activity to supplement that existing engagement rather than be tracked as a second, parallel thing alongside it.

What these have in common: the channel maps onto a relationship that's *already* being tracked elsewhere in the CRM, and Slack is just one more venue for the same relationship — not a new one. A broad, ongoing, many-member topic channel with no single external counterpart is the `standalone` case, and given the current public-channels-only scope, that's likely to be most of what you see.

If a channel name in the file doesn't exactly match one in `channels.json` (a typo, extra whitespace, wrong case) on a later run, the error message names the specific mismatch — fix it there and re-run rather than guessing at the cause.

This step is manual by design, not because it's technically hard — see `SKILL.md`'s "Step 1" for why deciding `standalone` vs. an existing Interaction is deliberately kept out of the pipeline's own hands.

## 2. (Optional) export the live People table

If you export the People table from Baserow as a CSV (with at least `name-person`, `email-1`, `email-2` columns) and save it as `private/slack/slack-export-<yyyymmdd>/people-export.csv`, the pipeline picks it up automatically — no flag needed. It'll match Slack channel members to existing People rows by email and use their canonical name. Without it, every member is written under their Slack display name and flagged as unmatched — the run still completes either way, it's just less precise.

## 3. Run it — one command, one flag

From the `rcm-crm` repo root:

```bash
python3 .claude/skills/crm-slack-extraction/scripts/run_pipeline.py --date <yyyymmdd>
```

That's the whole command. `<yyyymmdd>` is the only thing you need to type — every path (the export folder, the channel-mapping CSV, an optional people-export CSV, and every output file) is derived from it automatically, following the "Path convention" layout above. **You don't need to type out the full paths yourself** — doing so (e.g. pasting a path like `private/slack/slack-export-<yyyymmdd>/channel-mapping-<yyyymmdd>.csv` with the angle brackets still in it) will fail, since that's documentation notation, not something the shell can resolve; `--date` alone is enough.

If you omit `--date` entirely, the script prompts for it interactively:

```
Slack export date (ISO YYYYMMDD, e.g. 20260907):
```

Either way, the date is validated as exactly 8 digits before anything else runs — a malformed date (e.g. `2026-09-07` with dashes) is rejected with a clear error rather than silently misreading it.

Override any individual path only if you need a non-standard layout:
- `--export-dir <dir>` — overrides the derived export folder.
- `--channel-mapping <csv>` — overrides the derived mapping-CSV path.
- `--people-export <csv>` — overrides the derived people-export path.

This single command:
1. On a first run for this date, generates the starter channel-mapping CSV and stops for review (see "First run" above) — review it, then re-run the exact same command.
2. Validates the export against the mapping CSV (stops with the exact mismatch named if anything doesn't line up).
3. Matches channel members against the People export, if one exists at the derived path or was given via `--people-export`.
4. Writes `candidates-<yyyymmdd>.csv` next to the mapping CSV.
5. Writes `flagged-unmatched-users-<yyyymmdd>.csv` (same folder) if anyone couldn't be matched.
6. Runs `build_workbook.py` itself, producing the final xlsx (same folder).

You'll see a printed summary of channel counts, unmatched users, and any channel that needs its *existing* Interaction's notes updated by hand (see below).

## What you'll get back

All written inside `private/slack/slack-export-<yyyymmdd>/`, alongside the mapping CSV:

- `candidates-<yyyymmdd>.csv` — the intermediate fact-by-fact file. Includes a **People row for every unique Slack user found across all mapped channels** — see "Known limitation" below before treating this as a clean, ready-to-import list.
- `flagged-unmatched-users-<yyyymmdd>.csv` — only written if at least one channel member couldn't be matched to an existing person.
- `crm-extraction-output-<yyyymmdd>.xlsx` — the final workbook: a "READ FIRST" sheet first (see "Known limitation: column order" below), then the five data sheets, uncertain cells highlighted yellow — plus one additional worksheet per standalone channel, a plain alphabetical list of that channel's participants, for easy copy/paste into Baserow.

Plus a row-count summary printed to the terminal.

## Known limitation: column order does not match Baserow

The columns in each data sheet of the output xlsx are **not** in the same order as the live Baserow tables' on-screen columns. An earlier version of this skill tried to track Baserow's exact on-screen order (confirmed by manually screenshotting each table), so a row range could be pasted straight across without realigning — that's been dropped, because keeping a screenshot-derived order in sync with the live tables wasn't robust, and hardcoding one fixed order made it harder for anyone templating their own Baserow instance from RCM's to reorder their own columns freely. **Before pasting a row range into Baserow, check each column lines up by header name, not by position** — the workbook's first sheet ("READ FIRST") repeats this warning. Baserow's own Import feature can match incoming columns to existing fields by header name automatically, which would remove this manual-alignment step — that hasn't been implemented here and is scoped as a future development opportunity.

## Known limitation: no existing-CRM dedup

The People sheet in the output xlsx is a **full list of everyone found in the Slack export's mapped channels — it is not checked against the live CRM at all.** Some of these people are almost certainly already in Baserow. This is deliberate for the current deployment: a proper check would need either a fresh People-table export cross-referenced by email (goes stale immediately) or a live query against the Baserow API per person (not implemented). Review this sheet by eye against what you already know before adding anyone to Baserow, to avoid creating duplicates. **Querying the Baserow API to check for an existing match is a reasonable next development step** if this becomes impractical to do by eye at scale — not built into this deployment.

## What happens next (manual, by design)

Open the xlsx and manually add the rows into Baserow, same as any other extraction skill's output. Baserow's native **unique value constraint** on the relevant fields, if set up, will catch anything already in the CRM at that point — this pipeline deliberately does no duplicate-checking of its own.

For any channel mapped to an **existing** Interaction rather than `standalone` (listed in the run's printed summary), nothing is written to the xlsx for it at all — there's currently nothing to add to that Interaction's `notes` either, since the discussion-summary step is parked (see `SKILL.md`). Update that Interaction's notes by hand from your own knowledge of the channel, if you want to record anything there for now.

Check `flagged-unmatched-users-<yyyymmdd>.csv` (if written) and decide by hand whether each unmatched person is an existing CRM contact under a different email, or genuinely new.

## If lead-signals or discussion-summary get reinstated later

Both would reintroduce an LLM step for the first time in this skill's life. `references/local-llm-setup.md` documents the local Ollama/Qwen setup for that scenario, including a note on why a single scoped completion call (rather than full Claude Code agentic orchestration) is the intended shape for the summary step specifically — worth reading before rebuilding either feature, not just for historical interest.
