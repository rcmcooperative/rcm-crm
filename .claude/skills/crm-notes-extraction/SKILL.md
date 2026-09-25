---
name: crm-notes-extraction
description: Extract People/Organisations/Projects/Communities/Interactions entries for RCM Cooperative's Baserow CRM from a meeting-notes markdown file, producing an import-ready xlsx with uncertain fields flagged. Use this whenever Cass asks to "extract for the CRM", "run the extraction", or hands over a meeting-notes document (e.g. a file named meeting-something.md). This is designed to run entirely locally (claude-local / Qwen) — no note content should be sent to any external API. Duplicate-checking is NOT part of this skill — it is intended to be handled natively inside Baserow itself (via unique value constraints on the relevant fields), so this skill never needs a local copy of the existing CRM data.
---

# CRM Notes Extraction

Turns one meeting-notes markdown file into new/updated rows for RCM Cooperative's Baserow CRM, output as an xlsx ready for manual import into Baserow (where a native unique value constraint on the relevant fields, if set up, will catch any duplicates at that point).

This skill exists to run **entirely on-device** (via `claude-local`, Qwen3/Ollama) because meeting notes may be confidential (e.g. funder conversations, personal details, email summaries). Do not call any external API, web-search tool, or cloud model as part of this skill. If a step seems to require internet access (e.g. looking up an organisation's legal form), stop and flag it for Cass to check herself — do not guess and do not go online.

**Duplicate-checking is out of scope for this skill.** Earlier versions of this skill included a local fuzzy-match step against a full CRM export; that has been deliberately removed.

**TODO (Baserow duplicate-checking — not yet implemented, revisit once more real data is in):**
- Baserow supports **single-field unique value constraints** natively — set on a field, this blocks row creation outright if the value already exists (a stronger mechanism than SeaTable's Forms-only "prevent duplicates," since it applies regardless of entry point). Confirmed from Baserow's own docs: empty values are always exempt — only *populated* values must be unique.
- Baserow has **no native compound/multi-field unique constraint**. Their own documented workaround: create a Formula field concatenating the fields you want jointly unique, then apply the unique constraint to that formula field instead.
- Planned approach once set up: (1) a plain unique constraint directly on People's `email-1` — safe, catches real re-entries, never risks blocking two different same-named people since it doesn't look at name at all; (2) optionally, a compound `name + email` formula field as a second layer — but this has a known limitation worth remembering: since the formula still computes to a real string even when email is blank, two genuinely different same-named people who **both** lack an email on file would collide and the second would be wrongly *blocked*, not just flagged — treat any block from this second layer as "go verify," not as reliably correct.
- Case-sensitivity of Baserow's constraint is unconfirmed either way — worth testing directly before relying on it (same open question SeaTable's version had).
- **Softer alternative worth trying instead of/alongside a hard block, deliberately left unresolved for now**: Baserow's own documented technique for a non-blocking duplicate *warning* — a self-referencing Count field (link the field back to the same table, matched/filtered by that field's own value; a Count of 2+ signals a possible duplicate without preventing the row being saved). Could apply this to `name-person` (or a compound formula field) as a visible flag, separate from — and compatible with — a hard unique constraint on `email-1`. Not yet set up; setting it up will require re-exporting the field-definitions JSONs afterward, since it changes the live structure.
- None of this is set up on the live base yet — this section documents the plan and what's known, not a completed setup.

This skill should never ask for, read, or retain a copy of the existing CRM data — only the meeting notes are needed as input. Do not reintroduce a local dedup step without Cass explicitly asking for one.

Because this runs on a smaller local model, prefer mechanical rule-following over open-ended judgement. When a rule doesn't clearly resolve a case, flag it rather than guessing — see "When to flag instead of deciding" below.

**Path convention — read this before touching any file.** Every path in this document is written out in full, relative to the **repo root** (the directory `claude-local` was launched from). None of them are relative to this skill's own folder, even the ones that point at files inside this skill's own folder. Do not shorten any path or try to reconstruct a "relative to the skill" version — always use exactly what's written:
- Notes and outputs: `private/meeting-<name>.md`, `private/candidates-<name>.csv`, `private/crm-extraction-output-<name>.xlsx` — a top-level folder at the repo root, alongside `.claude/`, not inside it. Output filenames are derived from the input notes filename (see Step 4) — never fixed names, since Cass may process several notes files in one session.
- This skill's own reference docs and script: `.claude/skills/crm-notes-extraction/references/schema.md`, `.claude/skills/crm-notes-extraction/scripts/build_workbook.py`, etc.

## Step 0: Confirm every file exists before doing anything else

Before reading or writing anything else, check that these exact paths exist (e.g. with a directory listing or an attempted read of each) — do not skip this, and do not proceed past a missing file by guessing where it might actually be:

- `.claude/skills/crm-notes-extraction/references/schema.md`
- `.claude/skills/crm-notes-extraction/scripts/build_workbook.py`
- The meeting-notes file you were asked to extract from (a `private/meeting-...md` path)

If any of these can't be found at exactly the path given, **stop and report back to Cass** which specific path failed, rather than guessing an alternative location, searching elsewhere, or asking her an open-ended question about "the correct path." A wrong guess here is what has caused real problems before.

## Before you start

1. Read `.claude/skills/crm-notes-extraction/references/schema.md` in full — it has the exact column names for all five tables, the fixed picklist values, and the field-by-field extraction rules. Do not invent column names or picklist values not listed there.
2. If you haven't already confirmed Ollama/Qwen3 is installed and reachable on this machine, see `.claude/skills/crm-notes-extraction/references/local-llm-setup.md` first. For how this skill is actually invoked end-to-end, see `.claude/skills/crm-notes-extraction/references/how-to-run.md`.
3. Confirm you have:
   - The meeting-notes markdown file, at `private/meeting-<name>.md`. One or more meetings, possibly spanning several dates.
   - Attendee lists for each meeting. If a meeting's Attendees section is an image/media-tag rather than text, **stop and flag it** — list the meeting date and ask Cass for the image content or a text list. Do not proceed to build a People list for that meeting from body-text mentions alone until you've asked.

## Step 1: Read the notes, one meeting at a time

**The whole file is one Interaction, regardless of how many dated `# Meeting yyyy-mm-dd` sections it contains.** A notes file is about one topic (often a project) — even when that topic's meetings happen on separate dates, with different attendees each time (someone joining for just one instalment, say). Do not create a separate Interactions row per dated section within the same file. This applies even when attendees or the immediate discussion topic vary between dates within the file — the file-level subject is what defines the Interaction, not any single date's specifics.

For each `# Meeting yyyy-mm-dd` section (still read individually, for accurate People/attendee tracking per date):
- Record attendees (and apologies with a name given) — these are your only candidate People for this meeting.
- People merely mentioned in the discussion body, but not listed as present, are NOT candidates — unless they are directly quoted speaking in a multi-person call whose Attendees list is unreadable (see above — this itself should have already been flagged and resolved with Cass before you reach this point).
- Note the primary Organisation(s) and Project(s) actually under discussion. A passing list of partner names (e.g. "current partners: X, Y, Z, W") is not "primary" — record it as a text note on the Project instead of creating an Organisation row for each.
- Note any Communities mentioned, even in passing — these can be added regardless of whether they're the primary topic.
- If the same date appears twice with different attendees/content, treat them as two separate meetings for attendee-tracking purposes (do not merge the attendee lists) — but they still both belong to the same one file-level Interaction.

## Step 2: Cross-reference within this note file

Before treating two names as different people, check whether the notes themselves resolve it — e.g. someone referred to only by first name in one meeting may be given a full name in another meeting in the *same file*. Use full names once you can confirm them this way.

Do not attempt to resolve a first-name-only reference by guessing a surname. Leave it as first-name-only and flag it.

## Step 3: Build candidate rows

Follow `.claude/skills/crm-notes-extraction/references/schema.md` field-by-field. Reminders on the recurring conventions:
- People **notes** field: interest-area/background info only (what the person said about themselves/their expertise). Never put "what the meeting was about" here.
- Node-reconciliation: an entity only gets a row in a second table (e.g. an org that's also a community) if there's a genuine, fillable relationship-shape for it there (real people-leads/participants/outputs to record) — not just because the name could fit both tables. If unsure, flag it rather than creating the second row yourself.
- Any field you cannot fill from what's directly stated in the notes: leave the cell blank and mark it in the flagged-fields list (see Output format). Never fill a field with an inference you can't point to a specific line for.

## Step 4: Write candidates-<name>.csv

**Do not write the xlsx yourself.** Instead, write one fact at a time to a CSV file, and hand it to `.claude/skills/crm-notes-extraction/scripts/build_workbook.py`, which deterministically builds the correctly-formatted, correctly-headered xlsx for you. This keeps your job to "describe what's in the notes," not "figure out how to construct a formatted spreadsheet" — read that script's module docstring in full before writing this file; it has the exact format, a worked example, and the full list of valid column names per table.

The format is deliberately as simple as possible: **one line per fact**, four columns — `table,row,column,value`. Write a line only for something you actually found; never write a line to represent "I don't know this." A schema column with no line for a given person/org/etc. is automatically left blank and flagged in the output — that's the entire mechanism, nothing else to do. Do not try to write a "complete row" with empty placeholders for unknown fields — just don't write those lines at all.

`row` is a plain number that groups every fact about the same entity together — e.g. every line about the same person uses the same `row` number; the next person uses the next number. Row numbers reset per table (People row 1 and Organisations row 1 are unrelated).

Never write a line whose `column` is one of the columns `.claude/skills/crm-notes-extraction/scripts/build_workbook.py` rejects (auto-computed formula columns, Baserow system fields, or fields explicitly out of scope for this skill) — see that script's `FORBIDDEN_COLUMNS` dict, and `references/schema.md`, for the current per-table list. The script will reject the file if you do.

**Naming — derive from the input notes file, don't use a fixed name.** If the notes file is `private/meeting-<name>.md`, save this file as `private/candidates-<name>.csv`. For example, `private/meeting-CRUK-Manchester-ELNs.md` → `private/candidates-CRUK-Manchester-ELNs.csv`. This matters when Cass is processing more than one notes file — a fixed filename would silently overwrite the previous file's output. When processing several notes files in one session, do this whole Step 1 through Step 5 sequence separately and completely for each file before starting the next one, each with its own derived filenames throughout.

Every fact extracted from the notes goes in as a candidate — this skill does not try to determine whether an entity already exists in the live CRM (it has no access to the live data to check that against). Baserow's own duplicate-catching (unique value constraints, once set up — see the note above) is what's meant to handle that at the point Cass adds each row.

One partial exception: if the notes describe further activity on a meeting series that's clearly ongoing (e.g. another instalment of the same topic), it's fine to note that explicitly as the Interactions `notes` value (e.g. "this extraction covers the 2026-08-14 and 2026-08-28 meetings") so Cass can see at a glance whether to treat it as a new series or fold it into an existing one — but don't guess at an existing row's other field values.

## Step 5: Run the build script

```
python3 .claude/skills/crm-notes-extraction/scripts/build_workbook.py private/candidates-<name>.csv private/crm-extraction-output-<name>.xlsx
```

Using the same `<name>` derived in Step 4 for both the input and output filenames — e.g. `python3 .claude/skills/crm-notes-extraction/scripts/build_workbook.py private/candidates-CRUK-Manchester-ELNs.csv private/crm-extraction-output-CRUK-Manchester-ELNs.xlsx`. Run this from the repo root.

If it prints validation errors, they will name the exact line number and problem — fix the CSV and re-run. Do not try to hand-edit the xlsx or work around a validation error; fix the CSV so it matches the schema.

If it succeeds, it prints a confirmation with sheet and row counts — check these against what you expected from your own reading of the notes before reporting back to Cass.

## Output format

At the end, give Cass:
1. The xlsx file (`private/crm-extraction-output-<name>.xlsx`, per Step 5).
2. A short summary: how many new/updated rows per table.
3. A **flagged items list** — every field you left blank/highlighted, and why (one line each).

Duplicate-checking happens when Cass imports these rows into Baserow — via a native unique value constraint on the relevant fields, once confirmed/set up (see the note under "Duplicate-checking is out of scope" above) — do not attempt to pre-empt that here.

## When to flag instead of deciding

Always flag rather than deciding when:
- A meeting's attendee list is unreadable (image/media-tag).
- A name could plausibly be the same person as an existing record, but affiliations/context don't clearly confirm it.
- An entity might warrant a second node in another table, but you're not sure the relationship-shape is genuinely fillable yet.
- A field's format isn't established by precedent elsewhere in the CRM (e.g. no existing row shows what format a given field expects).
- Anything requiring information not present in the notes themselves (do not go online, do not guess).
</content>
