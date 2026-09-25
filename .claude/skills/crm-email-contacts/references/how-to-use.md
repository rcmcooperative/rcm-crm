# How to use: crm-email-contacts pipeline

Everything below runs in a terminal (bash). This pipeline is pure Python —
no LLM step is involved anywhere in it (see SKILL.md, "Does this use an
LLM?"). Run the stages in order; stage 5 is a manual pause where a human
reviews a spreadsheet before anything is written.

**Run everything from the repo root**, not from inside the skill folder.
The commands below assume that and use the skill's full path,
`.claude/skills/crm-email-contacts/scripts/pipeline.py`. Every path the
pipeline reads or writes (the `private/email-contacts/...` convention
below, and the output-colocation behaviour) is resolved relative to your
current directory, so running from anywhere else will look in the wrong
place.

**Outputs are written next to the data they came from.** If you use
`--date`, everything for that run lands in that dated folder. If you use
explicit paths instead (`--input`/`--contacts`/`--candidates`/`--people`)
without `--output`, each stage defaults to writing its result in the same
directory as the file it was primarily built from, rather than the repo
root or wherever you happen to be running from. `--output` always
overrides this if you want a result somewhere else.

## Folder convention

Exports are kept under the repo's gitignored `private/` folder, following
the same pattern as the other CRM data sources (`meeting-notes`, `slack`):

```
private/email-contacts/all-contacts-<DATE>/all-contacts-<DATE>/<export>.vcf
```

`<DATE>` is whatever date appears in the folder name, e.g. `20260905` for
a folder called `all-contacts-20260905`. The doubled inner folder is
Google Takeout's own archive-unzip nesting, kept as-is. Every stage of the
pipeline accepts a `--date` flag; when you pass it, the input/output paths
for that date's folder are worked out automatically, and `parse` will ask
you for the date interactively if you don't pass either `--date` or
`--input`. You can still pass explicit `--input`/`--contacts`/`--output`
paths at every stage if your files live somewhere else.

## 0. One-time setup

```bash
pip install vobject tldextract pandas openpyxl --break-system-packages
```

## 1. Export contacts from Google

Do this in a browser first, not in bash. Save/unzip the result into
`private/email-contacts/all-contacts-<DATE>/`, following the convention
above, where `<DATE>` is today's date (or whatever date you're labelling
this export run with).

```text
1. Go to contacts.google.com
2. Click "Other contacts" in the left sidebar
3. Select all entries (checkbox at the top of the list)
4. Click "Add to contacts" (icon in the toolbar once contacts are selected)
   — this copies auto-saved "Other contacts" into your real Contacts list,
   which is the only list Takeout exports by default
5. Go to takeout.google.com
6. Click "Deselect all"
7. Check "Contacts" only
8. Click through to "Create export"
9. Download the resulting archive and unzip it into
   private/email-contacts/all-contacts-<DATE>/ — you want the .vcf file
   inside the (doubled) folder structure described above
```

### 1a. Tidy contacts before exporting (do this before step 5 above)

Google's "Other contacts" auto-collection frequently creates a **separate
entry per email address** rather than one entry per person, and often
with no name attached at all (e.g. it only ever saw the raw address in a
Cc header, never a display name). A nameless entry looks like this in
`parsed_contacts.csv` — a blank `name` next to an otherwise normal email:

```
name,email,org_domain
,j.smith@example.ac.uk,example
```

This isn't a matching bug: `match_candidates.py` can only group and match
entries by name, so a genuinely nameless entry is silently skipped rather
than wrongly matched to someone — a safer failure mode than guessing, but
it means that email is lost unless it's fixed at the source. The pipeline
deliberately doesn't try to guess ownership from the email address itself
(e.g. spotting "smith" in `j.smith@example.ac.uk`) — that's exactly the
kind of inference this pipeline avoids, since it risks silently
misattributing addresses at organisations where surnames collide.

Before running Takeout, in Google Contacts:

1. Use **Merge & fix → Merge duplicates** — this catches cases where the
   *name* matches but the emails differ across entries
2. For entries with no name at all, Merge & fix can't suggest anything
   (there's nothing to compare against) — open the real contact card for
   that person, add the orphaned email as a second `EMAIL:` field directly
   on their card, then delete the nameless duplicate entry

Once a person's emails all live on **one contact card with multiple email
fields**, `parse_vcf.py` and `match_candidates.py` already handle that
correctly end to end — see the multi-email `email-1`/`email-2`/`email-3`
column behaviour below.

This tidying step is manual and takes real time on a large "Other
contacts" list, but it's worth treating as a genuine, ongoing part of
maintaining accurate data about the community — not a one-off chore to
rush through before a pipeline run. A merged, correctly-attributed
contact card stays useful long after this particular export.

## 2. Export the current Baserow People table

Also a browser step. Export the People table as CSV or XLSX (whichever your
usual Baserow export gives you), and note the exact column names for the
person's full name and their email field (e.g. `name-person`, `email-1`).
This file isn't part of the dated-folder convention — keep it wherever your
People exports normally live, and pass its path with `--people`.

## 3. Parse the .vcf into a plain CSV

Run from the repo root:

```bash
python .claude/skills/crm-email-contacts/scripts/pipeline.py parse --date 20260905
```

This resolves the `.vcf` from `private/email-contacts/all-contacts-20260905/`
automatically and writes `parsed_contacts_20260905.csv` into the same
folder. If you don't pass `--date` (or `--input`), you'll be asked for the
date interactively. To bypass the convention entirely and point at a
specific file:

```bash
python .claude/skills/crm-email-contacts/scripts/pipeline.py parse \
    --input path/to/contacts.vcf
```

With no `--output`, this writes `parsed_contacts.csv` into
`path/to/` — the same folder the `.vcf` came from. Pass `--output`
yourself to write somewhere else.

Output columns: `name, email, org_domain`. One row per email address — a
contact with two emails produces two rows. `org_domain` is derived from
the email address itself (e.g. "UCL" from alice@ucl.ac.uk, "Stanford"
from alice@stanford.edu), title-cased by default and fully upper-cased
for known acronyms, with known personal/webmail domains (gmail.com,
outlook.com, etc.) left blank. It's not matched against Baserow's
Organisations table — it's a reference value only, for the human review
step below. (The vCard's own ORG field is not read or output at all.)

## 4. Generate ranked match candidates

```bash
python .claude/skills/crm-email-contacts/scripts/pipeline.py match \
    --date 20260905 \
    --people baserow-export-people-20260907.xlsx \
    --people-name-column "name-person" \
    --people-email-column "email-1" \
    --people-org-column "organisations"
```

With `--date` given, `--contacts` and `--output` default to
`parsed_contacts_20260905.csv` and `candidate_matches_20260905.xlsx` in
that same dated folder. Without `--date`, pass `--contacts` explicitly;
`--output` then defaults to `candidate_matches.xlsx` in the same folder as
`--contacts`.

- `--people` accepts `.csv` or `.xlsx`
- `--people-name-column` / `--people-email-column` / `--people-org-column`
  must match your actual Baserow export's column headers exactly
  (`--people-org-column` defaults to `organisations`, the People table's
  link field to Organisations)
- `--min-score` (0–100, default 60) filters out very weak matches — lower
  it if you're missing matches you expect to see, raise it if the
  candidate list is too noisy
- A person is only skipped entirely if they already have **both** an
  email and an organisation — missing either one is enough to include
  them, so someone with an email already can still surface an
  `org_domain`, and someone with an organisation already can still
  surface an email. The two are filled independently at apply time, and
  confirming a row never overwrites whichever one the person already has
- **Every contact is represented, not just ones matched to an existing
  Baserow person.** A contact with no name match anywhere in the People
  export still gets a row, with `in_crm` set to `0` and `baserow_name`
  left blank — confirming it tells the next step to add them as a
  brand-new person rather than update an existing one

Output columns: `baserow_name`, `in_crm`, `matched_contact_name`,
`matched_contact_org_domain`, `match_score`, `runner_up_score`,
`already_has_email`, `already_has_org`, one or more `email-1`, `email-2`,
`email-3`, ... columns (as many as the busiest match needs — most rows
will have fewer filled in), and a blank `confirm` column, sorted by match
score (rows with no match, `in_crm=0`, sort to the bottom). The email-N
naming matches the Baserow People table's own convention, so a confirmed
row applies straight across with no reshaping.

## 5. Review the candidates (manual — do this in Excel/Sheets, not bash)

Open `candidate_matches_<DATE>.xlsx` (or `candidate_matches.xlsx`, if you
ran without `--date`):

- For each row, compare `baserow_name` against `matched_contact_name` and
  decide whether it's really the same person
- Check `in_crm` first: `1` means this contact matched someone already in
  Baserow (review as a match, using `already_has_email`/`already_has_org`
  to see what's actually being proposed); `0` means this contact wasn't
  found anywhere in the People export — confirming it adds them as a new
  person, so check the name/email look right before doing so
- Check `already_has_email` / `already_has_org` (for `in_crm=1` rows) to
  see what's actually being proposed — a row can be here purely to
  surface an organisation for someone who already has an email, or
  purely for an email for someone who already has an organisation
- `matched_contact_org_domain` is a raw email-domain label, not a
  Baserow Organisations record — it feeds the Organisations sheet built
  in the next step, but nothing here writes to Baserow's Organisations
  table automatically
- Type `yes` in the `confirm` column for rows you accept
- If a contact had multiple emails, they're already split across
  `email-1`, `email-2`, etc. — edit or blank out any of them if one's
  wrong, or leave as many as you want applied
- **Do this for every row, even a `match_score` of 100** — this is the
  pipeline's one and only judgment-call checkpoint, and it's a human
  making it, not a script or a model
- Save the file in place (same filename), so the next command finds it
  automatically via `--date`

## 6. Apply confirmed matches

```bash
python .claude/skills/crm-email-contacts/scripts/pipeline.py apply \
    --date 20260905 \
    --people baserow-export-people-20260907.xlsx \
    --people-name-column "name-person"
```

With `--date` given, `--candidates` and `--output` default to
`candidate_matches_20260905.xlsx` and `people_export_updated_20260905.xlsx`
in the dated folder. Without `--date`, pass `--candidates` explicitly;
`--output` then defaults to `people_export_updated.xlsx` in the same
folder as `--people` (since the output is an updated copy of that file's
data). Reads only the rows where `confirm` is `yes` (case-insensitive).

For `in_crm=1` rows: writes every `email-N` column found in the
candidates file into the matching `email-N` column on a **copy** of
`baserow-export-people-20260907.xlsx` — creating that column on the
People side if it doesn't already exist, and never overwriting an email
that's already there — leaving every unconfirmed or already-populated
row untouched.

For `in_crm=0` rows: appends a brand-new row instead — name and email(s)
filled in from the contact, everything else left blank for you to
complete before pasting into Baserow.

The output file has two sheets:

- **People** — the updated export, with emails applied to existing rows
  and any confirmed new people appended at the end. Column order is
  whatever the input `--people` file already had, with any new columns
  (e.g. a new `email-N` slot) appended at the end
- **Organisations** — populated with the distinct `org_domain` values
  found among this run's confirmed matches (deduplicated, into
  `name-org-long`), plus a handful of other useful Organisations fields
  as blank columns to fill in if needed. This is a starting-point
  candidate list from this batch, not a full/deduplicated-against-Baserow
  Organisations export — check for existing matches before adding to the
  live table. Column order here is just this skill's own plain reading
  order (names, then description, then links) — not derived from
  Baserow at all

**⚠️ Column order is NOT matched to Baserow's live on-screen order in
either sheet.** An earlier version of this pipeline tried to maintain a
hardcoded, screenshot-derived order list, but that turned out not to be
robust — Baserow's field-definitions API doesn't expose true on-screen
position, so the list needed manual re-screenshotting whenever the
schema changed, and it already went stale once as new fields were added.
Dropping it also means this pipeline won't impose a specific column
order onto anyone else's Baserow instance if this base is ever templated
elsewhere with columns in a different order. The practical consequence:
**before pasting into Baserow, you'll need to manually check/reorder
each sheet's columns in Excel against a current screenshot of the live
table.** Pasting a misaligned range will silently write data into the
wrong fields. (Baserow's own import feature can match by column header
name instead of position, which would remove this problem entirely — not
being pursued now, scoped as further development.)

## 7. Copy-paste into Baserow (manual)

Open the resulting `people_export_updated...xlsx`. **First, for each
sheet, check/reorder its columns in Excel against a current screenshot
of the corresponding live Baserow table** (see the warning above — this
step is no longer done for you). Then copy each sheet's populated range
and paste it into the corresponding live Baserow table — **People** into
the People table, **Organisations** into the Organisations table (after
checking those organisations don't already exist there).

## Alternative: the combined `fill` path (no review spreadsheet)

Instead of steps 4–6 above, `fill` does extraction (if needed) + matching
+ writing in one command. Use this when the reviewed path's per-row
confirmation isn't practical for the volume involved, and reviewing the
*output* (via the yellow highlighting) is an acceptable substitute for
confirming each match beforehand.

**Matching here is exact-normalised, not fuzzy/scored** — deliberately
stricter than `match`, since there's no human checkpoint to catch a wrong
fuzzy match. Two names only match if they're identical after
lower-casing, punctuation-stripping, and word-order normalisation (so
"Smith, Bob" still matches "Bob Smith", but "Bob Smith" won't match "Rob
Smith" or "Bob Smyth").

```bash
# Parse a .vcf and fill in one step:
python .claude/skills/crm-email-contacts/scripts/pipeline.py fill \
    --date 20260907 \
    --people baserow-export-people-20260907.xlsx \
    --people-name-column "name-person"

# Or reuse an already-parsed contacts CSV:
python .claude/skills/crm-email-contacts/scripts/pipeline.py fill \
    --contacts parsed_contacts_20260907.csv \
    --people baserow-export-people-20260907.xlsx \
    --people-name-column "name-person" \
    --output baserow-export-people-20260907-emails-added.xlsx
```

With `--date` given (and no `--contacts`), this resolves and parses the
`.vcf` itself — no separate `parse` run needed first. `--output` defaults
to the dated folder (with `--date`) or alongside `--people` otherwise,
same as the other stages.

**What it does:**

- Fills existing blank `email-1`/`email-2`/`email-3`/... slots first, in
  order; only creates a new `email-N` column once every existing slot is
  full for at least one row; never re-adds an email already present
  anywhere in that row
- Fills a blank `org_domain` column (creating it if the People export
  doesn't already have one) — never overwrites an existing value
- **Ambiguous names**: if two or more rows in the People export share the
  same normalised name, none of them are touched — there's no reliable
  way to know which one a contact's email belongs to. Those rows are
  highlighted **yellow** in the output so you can resolve them manually.
- **Unmatched contacts**: a contact name that doesn't match anyone in the
  People export is appended as a new row at the end — filled in as best
  it can (name, email(s), org_domain; everything else blank) — and
  highlighted **yellow**, since it's new and unverified.
- **New columns**: any column this run added (a new `email-N` slot, or
  `org_domain` if it didn't exist before) is highlighted **yellow**
  across its whole header and column, so it's obvious what changed
  structurally.

After running, review the yellow-highlighted rows/columns in the output,
then copy-paste into Baserow as in step 7 above.

## Troubleshooting

- **`No .vcf file found for date '...'`** — check the folder actually
  exists at `private/email-contacts/all-contacts-<DATE>/` (and its inner
  doubled folder) and that `<DATE>` matches exactly, digits only. Also
  check you're running from the repo root — this path is resolved
  relative to your current directory.
- **`Found more than one .vcf file for date '...'`** — the folder has more
  than one `.vcf` in it; pass `--input` with the exact file to use.
- **`Column '...' not found`** — the `--people-name-column` value doesn't
  match the export's actual header. Re-check the exact column name in the
  file (case and hyphenation matter).
- **`No email-N columns found`** (from `apply_matches.py`) — the
  candidates file doesn't have any `email-1`/`email-2`/... columns; check
  you're pointing at a file produced by `match_candidates.py` and haven't
  renamed those columns during review.
- **Candidate file has 0 rows** — either every Baserow person already has
  an email (nothing to do), or `--min-score` is set too high for the real
  data; try lowering it.
- **A name you expected to match doesn't appear** — check
  `parsed_contacts_<DATE>.csv` directly; if the contact isn't there, it may
  still be sitting only in Google's "Other contacts" list rather than added
  to Contacts before the Takeout export (see step 1).
- **An email you expected is missing, but the contact's name IS present in
  `parsed_contacts_<DATE>.csv` on a different row with no name** — this is
  the split-entry / nameless-entry issue described in step 1a. Merge that
  email onto the real contact card in Google Contacts and re-export.
- **A row I expected `fill` to update is untouched and NOT highlighted
  yellow** — check whether its normalised name collides with another row
  in the same People export (the ambiguous-name case); if so it would be
  highlighted, so more likely the contact's name genuinely doesn't match
  exactly (e.g. a nickname, middle initial, or spelling difference) —
  `fill` won't fuzzy-match, so use the reviewed `match`/`apply` path
  instead for names like these.