# How to Run This Skill

This skill combines model reasoning (reading and interpreting the notes) with a deterministic script (`.claude/skills/crm-notes-extraction/scripts/build_workbook.py`, building the actual xlsx from a CSV the model produces) — see `SKILL.md` Steps 4–5. "Running" it means invoking `claude-local` (or `claude-cloud`) with the right input; the model then writes `private/candidates-<name>.csv` and runs the script itself as its final step. Output filenames are derived from the input notes filename, so it's safe to process several notes files without one overwriting another's output.

## 1. Place the skill at `.claude/skills/` in the repo root

Claude Code auto-discovers project skills from a `.claude/skills/` folder **directly under the directory you launch it from**. So this skill needs to live at:

```
<rcm-crm repo root>/.claude/skills/crm-notes-extraction/
```

(i.e. `SKILL.md` and `references/` sit inside that `crm-notes-extraction` folder, which itself sits inside `.claude/skills/`, which sits at the repo root — not nested any deeper).

One thing worth knowing: if `.claude/skills/` is nested *below* wherever you actually launch Claude Code from, those skills only load lazily — the first time Claude touches a file in that subdirectory, not at startup. As long as you follow step 2 exactly (launch from the repo root itself), this doesn't apply and the skill loads immediately.

## 2. Confirm the local LLM is up

See `.claude/skills/crm-notes-extraction/references/local-llm-setup.md` if you haven't already — steps 1–7 (Ollama installed, service running, model pulled, claude-local profile created, context window fixed on both sides, claude-local opened, confirmed running locally via `/status`).

## 3. Run it

```bash
cd <path-to-rcm-crm-repo>
claude-local
```

Then, in the session, give it the meeting-notes file and ask for the extraction. Natural-language triggers (e.g. "extract CRM entries from...") should work, but proved unreliable in testing on `qwen-coder-local` specifically — being fully explicit is more reliable, especially on a coder-tuned model:

```
Follow the crm-notes-extraction skill: read .claude/skills/crm-notes-extraction/references/schema.md, then extract entries from private/meeting-CRUK-Manchester-ELNs.md following SKILL.md's Step 0 through Step 5, then write private/candidates.csv and run .claude/skills/crm-notes-extraction/scripts/build_workbook.py to produce the xlsx. Note: private/ is a top-level folder at the repo root; the skill's own files (schema.md, build_workbook.py) live inside .claude/skills/crm-notes-extraction/ — use the full paths above exactly as written, don't shorten them.
```

Meeting notes live in `private/` **at the repo root** — a top-level folder alongside `.claude/`, not inside the skill's own directory (`.claude/skills/crm-notes-extraction/`). This has tripped the model up before, so if a run reports it can't find a `private/...` file, check it hasn't constructed a path like `.claude/skills/crm-notes-extraction/private/...` — that's always wrong. You don't need to attach anything else — no CRM export, no ledger, no contact list. The notes file is the only input this skill needs (see SKILL.md's "Before you start").

**Processing several notes files in one prompt:** be explicit that each should be handled as its own complete pass (Steps 1-5 in full) before starting the next, since that's what makes the derived-filename convention in Step 4 actually get followed correctly:

```
Using the crm-notes-extraction skill, process each of these meeting-notes files completely, one at a time, before starting the next: private/meeting-a.md, private/meeting-b.md, private/meeting-c.md.
```

The skill's own Step 4 naming rule (derive `candidates-<name>.csv` and `crm-extraction-output-<name>.xlsx` from each input filename) should keep every file's output separate without needing to spell out the exact filenames yourself — but it's worth checking all expected output files exist afterward on the first batch run you try, same as any new pattern.

## What you'll get back

- `private/candidates-<name>.csv` — the model's fact-by-fact description of what it found (intermediate file, not the deliverable itself), one per notes file processed.
- `private/crm-extraction-output-<name>.xlsx` — one workbook per notes file processed, five sheets (People, Organisations, Communities, Interactions, Projects), with any uncertain cells highlighted yellow. Built deterministically by `.claude/skills/crm-notes-extraction/scripts/build_workbook.py` from the CSV above — never written directly by the model.
- A short summary of new/updated row counts per table.
- A flagged-items list explaining every highlighted cell.

## What happens next (manual, by design)

Open the xlsx and manually add the rows into Baserow, same as you've been doing with the hosted-chat extractions. Baserow's native **unique value constraint** on the relevant fields — if set up (see `references/schema.md` and the note in `SKILL.md`) — will catch anything that's already in the CRM at that point; this skill deliberately does no duplicate-checking of its own.

## First time using this on a given machine

Before trusting it on real, possibly-confidential notes, run the sanity check described in `.claude/skills/crm-notes-extraction/references/local-llm-setup.md` step 8 — compare its output against a note-set you've already extracted via hosted Claude (Superbloom or CRUK-Manchester-ELNs), and check attendee-only People, flagged-not-guessed uncertain fields, and correct picklist values.
