---
name: crm-email-contacts
description: Match email addresses from an exported Google Contacts .vcf file against a Baserow People table export, to fill in missing emails on existing CRM records. Use when the user wants to populate missing People emails from Google Contacts, mentions a .vcf export, or asks to match/reconcile Google Contacts against the RCM Cooperative Baserow CRM. Code-only skill — pure Python, no LLM involved (same framing as the CRM-from-Slack import skill); see "Does this use an LLM?" below.
---

# Google Contacts Email-Matching Pipeline

**Skill type: code only — no LLM.** This is a collection of deterministic
Python scripts, not an LLM-driven workflow — the same framing used for the
CRM-from-Slack import skill. It lives under `.claude/skills/` as a place to
collect and re-run scripts, not because a model interprets anything in it.

Matches email addresses from an exported Google Contacts `.vcf` file against
existing People records in a Baserow CRM export, so records missing an email
can be filled in — via plain Python string parsing and comparison, with a
human confirming every match before anything is written back.

## When to use this

- The user has exported Google Contacts (or "Other contacts") as a `.vcf`
  file and wants those emails matched against Baserow People records
- The user wants to fill in missing `email-1` values in the People table
  from an email address book, without manually cross-checking every name

## Folder convention

Exports live in the repo's gitignored `private/` folder, alongside the
other CRM data sources (`meeting-notes`, `slack`):

```
private/email-contacts/all-contacts-<DATE>/all-contacts-<DATE>/<export>.vcf
```

`<DATE>` is whatever appears in the folder name (e.g. `20260905`). Every
stage takes an optional `--date` flag that resolves input/output paths
against this convention automatically; if you run the `parse` stage
without `--date` or `--input`, it asks you for the date interactively
rather than failing. See `references/how-to-use.md` for the full layout
and every stage's default paths.

**Run from the repo root, always.** All paths (the `private/...`
convention above, and explicit paths passed via flags) are resolved
relative to the current directory, so the pipeline must be invoked from
the repo root — e.g. `python .claude/skills/crm-email-contacts/scripts/pipeline.py
parse --date 20260905` — not from inside the skill folder itself.

**Outputs are written next to the data they came from.** When using
`--date`, everything for a run stays in that dated folder. Without
`--date`, each stage that isn't given `--output` explicitly defaults to
writing its result in the same directory as the file it primarily
operates on (e.g. `apply`'s output lands next to `--people`, since it's
producing an updated copy of that file), rather than the repo root or
wherever the command happens to be run from.

## Does this use an LLM?

**No.** Every step — parsing the vCard file, matching names, and writing
emails/org_domain into a spreadsheet — runs as deterministic Python
(stdlib `difflib` for fuzzy matching, `vobject` for parsing, `tldextract`
for domain extraction, `pandas`/`openpyxl` for reading, writing, and
highlighting spreadsheets). In the reviewed path (match → apply), the
only judgment call — deciding whether a matched name really is the same
person — is made by a human, in a spreadsheet, not a model. The `fill`
path has no human-review step at all, so it uses exact (not fuzzy)
name matching instead, and flags anything it can't resolve confidently
(ambiguous names, unmatched contacts) in yellow rather than guessing. If
this is ever extended to read data an LLM hasn't seen before (e.g.
resolving messier name variants) that would be a deliberate, separate
decision — not something the current scripts do.

## Two ways to run this

**Reviewed path (recommended for most runs): `match` → human review → `apply`.**
Fuzzy name-matching with a score, a spreadsheet checkpoint where a human
confirms every match before anything is written, one email address
proposed per column. See stages 4–6 below.

**Combined path: `fill`.** One command does extraction + matching +
writing in a single step, with no review spreadsheet in between. Matching
is exact-normalised (not fuzzy/scored) specifically because there's no
human checkpoint to catch a wrong fuzzy match — so it under-matches by
design rather than risks a silent wrong pairing. Anything it can't
resolve with confidence gets highlighted **yellow** instead of guessed
at: a Baserow person whose name collides with another Baserow person
(ambiguous — left untouched), and a contact that doesn't match anyone in
Baserow (appended as a new row, filled in as best it can). Any new
column created (a new `email-N` slot, or `org_domain` if the People
export didn't already have one) is also highlighted yellow across its
whole header and column. Use this when the volume makes the reviewed
path impractical and yellow-highlight review of the *output* is an
acceptable substitute for row-by-row confirmation beforehand.

## Pipeline stages

1. **Export contacts from Google** (manual, one-off per run) — see
   `references/how-to-use.md` for the exact Google Contacts / Takeout steps,
   including the "Other contacts" gotcha and the contact-tidying step
   (merging split/nameless entries) that should happen before export —
   the pipeline can't safely guess which nameless email belongs to whom,
   so that reconciliation work has to happen at the source.
2. **Export the current People table from Baserow** (manual, one-off per run).
3. **Parse the `.vcf`** — `python .claude/skills/crm-email-contacts/scripts/pipeline.py parse ...`
   (calls `scripts/parse_vcf.py`). Structured text parsing only.

**Reviewed path:**

4. **Generate ranked match candidates** — `python .claude/skills/crm-email-contacts/scripts/pipeline.py match ...`
   (calls `scripts/match_candidates.py`). Fuzzy name comparison; skips
   People rows that already have an email.
5. **Human review (required checkpoint)** — open the candidate spreadsheet,
   type `yes` in the `confirm` column for matches to accept.
6. **Apply confirmed matches** — `python .claude/skills/crm-email-contacts/scripts/pipeline.py apply ...`
   (calls `scripts/apply_matches.py`). Writes accepted emails into a copy of
   the People export, and populates an Organisations sheet from the
   `org_domain` values found among the confirmed matches. **Column order is
   not matched to Baserow's live layout** (dropped as not robust enough to
   maintain — see the script's docstring) — check/reorder columns in Excel
   against a current screenshot before pasting into either live table.

**Combined path (alternative to steps 4–6):**

4′. **Extract + match + fill in one step** — `python .claude/skills/crm-email-contacts/scripts/pipeline.py fill ...`
   (calls `scripts/fill_from_contacts.py`). Can take a `.vcf`/`--date`
   directly (parses fresh) or an already-parsed `--contacts` CSV. Exact
   name matching, no review spreadsheet; yellow-highlights anything
   uncertain in the output instead.

7. **Copy-paste into Baserow** (manual, matching the existing workflow).

`scripts/pipeline.py` is the single entrypoint for stages 3, 4, 4′, and 6 —
run it (from the repo root) with `--help` for the stage list, or
`<stage> --help` for a stage's full options. The individual stage scripts
(`parse_vcf.py`, `match_candidates.py`, `apply_matches.py`,
`fill_from_contacts.py`) still exist underneath and can be called directly
too; `pipeline.py` just wraps them under one command.

Full commands for every stage, including flags and expected output, are in
**`references/how-to-use.md`** — read that before running anything.

## Future development (not built yet)

The Google People API's `otherContacts.list` endpoint would let step 1 read
"Other contacts" directly and programmatically, removing the manual
"select all → add to Contacts" step. Deferred for now.
