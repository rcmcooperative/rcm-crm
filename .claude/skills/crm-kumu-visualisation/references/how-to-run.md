# How to run the Kumu export pipeline

## 1. Get the Baserow data

This pipeline expects five `.xlsx` files in `private/kumu/baserow-export/`,
named:

```
baserow-export-Communities-<DATE>.xlsx
baserow-export-Interactions-<DATE>.xlsx
baserow-export-Organisations-<DATE>.xlsx
baserow-export-People-<DATE>.xlsx
baserow-export-Projects-<DATE>.xlsx
```

`<DATE>` is whatever you like (e.g. `20260924`) — the pipeline picks the
lexicographically-last match per table if more than one is present, so a
`YYYYMMDD` date sorts correctly.

These need to contain actual **row data**, not just the field-definitions
structure. Use Baserow's own "Export table" feature (or the row-data API)
per table, saved with the naming convention above.

If you only need to check for schema drift (not run a real export):

1. Baserow → account → API tokens → create a new token, read-only, scoped
   to just this database if possible. Name it descriptively with purpose +
   date (e.g. `schema-check-readonly-20260924`).
2. `GET https://api.baserow.io/api/database/fields/table/{table_id}/` with
   `Authorization: Token YOUR_TOKEN`, once per table.
3. Compare the returned field names against `scripts/config.py`'s
   `EXPECTED_COLUMNS`. Update `config.py` if anything's changed.
4. Revoke the token immediately after use — treat it as single-use.

## 2. Run the pipeline

From the repo root:

```
python .claude/skills/crm-kumu-visualisation/scripts/pipeline.py
```

Optional flags:

```
--input-dir  private/kumu/baserow-export   (default)
--output-dir private/kumu/kumu-input       (default)
--date       YYYYMMDD                       (default: today)
```

**Read the warnings.** They cover two things that can't be silently
resolved: a link field naming something with no matching row (edge
skipped, not guessed), or two rows in the same table sharing an identical
label (edges naming that label are skipped rather than picking one
arbitrarily).

## 3. Import into Kumu

Drag either output workbook onto a Kumu map. Both `elements` and
`connections` sheets are read automatically, and re-importing an updated
export **updates** existing elements/connections rather than duplicating
them, since IDs are stable across runs (derived from Baserow's own row
`id`, which is never reused).

Use `kumu-import-internal-*.xlsx` for RCM Cooperative's own internal map,
and `kumu-import-public-*.xlsx` for anything shared outside the team.

`references/kumu-display-settings-internal` holds the Kumu `@controls`/
`@settings` code for the internal map's legend, filters, and showcase
controls — paste it into Kumu's Advanced Editor settings panel.

## Known assumptions and decisions (see schema.md for full detail)

- [x] Public-export consent handling excludes `consent-internal` /
      `consent-none` / `consent-not-asked` people entirely — confirmed by
      Cass (2026-09-24).
- [x] `notes`, `email-2`, `email-3` are internal-only, stripped from the
      public export for every Person regardless of consent tier — confirmed
      by Cass (2026-09-24).
- [x] All seven People "-user-nominated" fields are excluded from both
      exports. Reasoning split into two categories, per the authoritative
      policy Cass wrote for the content-extraction skill (confirmed applies
      here too, 2026-09-24): Category A (`orgs-`, `communities-lead-`,
      `communities-participant-`, `notes-user-nominated`) is permanently
      excluded as inherently-unreviewed staging data; Category B
      (`pronouns-`, `git-other-`, `socials-other-user-nominated`) is
      excluded only because Baserow has no reviewed-status field yet for
      this pipeline to gate on — see the "future development" note in
      schema.md for what would need to change to include them.
- [ ] `affiliated` edge type for `Communities.organisations` and
      `Projects.communities` — confirm these are genuinely distinct from
      the `sponsor` edges already captured, not duplicates of them.
- [ ] Relationship/edge fields for People are not filtered by consent tier
      at all currently (only profile fields are) — undecided whether a
      pseudonymised person's edges should also be restricted.
- [ ] Node sizing (Person 1, Project/Community 50, Organisation 100) and
      generic (not per-table-pair) edge typing are both first-pass choices,
      expected to be revisited once the map itself clarifies the
      Organisation/Community and Project/other-table boundaries.

## Planned future schema additions

- `mission-interest` / `mission-influence` (naming TBC) — new People fields
  for mapping a person's interest in / influence over RCM Cooperative's
  mission. Not built yet. Confirmed by Cass (2026-09-24): once added, these
  go straight into `config.PERSON_INTERNAL_ONLY_FIELDS` — never published,
  at any consent tier. See `config.py`'s comment above that list for the
  three-step checklist to follow when adding them.
