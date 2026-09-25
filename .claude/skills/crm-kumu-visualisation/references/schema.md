# Kumu export schema reference

This documents what `scripts/config.py` implements. If Baserow's schema
changes, update `config.py` first, then this file to match.

Source of truth for the current Baserow field list: the read-only
field-definitions API export, most recently taken 2026-09-24.

Eventual plan: fold this into the single shared CRM schema.md once that
consolidation happens across all CRM skills (crm-notes-extraction,
crm-email-contacts, this one). Kept as its own file for now so it's easy to
swap out later without touching pipeline logic.

## Node types (Kumu elements)

| Kumu Type      | Baserow table | Label field      | Size | Consent-gated? |
|----------------|---------------|-------------------|------|-----------------|
| Person         | People        | `name-person`     | 1    | yes (`mapping-consent`) |
| Organisation   | Organisations | `name-org`        | 100  | no — always public |
| Community      | Communities   | `name-community`  | 50   | no — always public |
| Project        | Projects      | `name-project`    | 50   | no — always public |

Every element also gets a `type-display` field. For most node types this is
just a plain duplicate of `Type` (Kumu treats `Type` as a reserved
structural field — element de-duplication via the elements sheet, default
styling — which conflicts with using it to drive legend/shape/color
formatting directly; same issue as in the old SharePoint-era MVP, same fix:
`type-display` is what `kumu-display-settings-*` files should reference for
any display/legend purpose, never `Type` itself).

For Organisations specifically, `type-display` instead takes its value from
`Organisations.type` (e.g. "Academic institute", "Non-profit"), so the
legend can distinguish organisation subtypes rather than lumping every
organisation under one generic label. Falls back to the plain "Organisation"
label (with a pipeline warning) if that field is blank on a given row. See
`config.TYPE_DISPLAY_SOURCE_FIELD` to extend this to other node types later
(e.g. Projects by `status`) without touching pipeline logic.

`type-display`'s colour mapping (in `kumu-display-settings-internal`'s
`element-color`) uses the **Tol Muted** colour-blind-safe qualitative
palette for the 9 Organisation subtypes; Person/Community/Project use
neutral black/dark-blue/grey tones instead, kept separate from the Muted
palette rather than mixed into it. Colours are pinned to literal
`type-display` values via Kumu's named `categorize()` syntax, not
positional order.

| Category | Hex |
|---|---|
| Person | `#000000` |
| Community | `#004488` |
| Project | `#666666` |
| Funder | `#CC6677` |
| Consortium | `#332288` |
| Academic institute | `#DDCC77` |
| Public sector / Government | `#117733` |
| Intergovernmental organisation | `#88CCEE` |
| Non-profit | `#882255` |
| Social enterprise | `#44AA99` |
| Cooperative | `#999933` |
| Private industry | `#AA4499` |

**Interactions are not Kumu elements.** All the role-specific rollups needed
(who led/participated/sponsored/funded an interaction) already exist as link
fields on the four tables above, so Interaction data is read from those
columns rather than by joining back to the Interactions table. Each becomes
a pipe-separated metadata list on the relevant node's profile:

| Node type    | Metadata field(s) |
|--------------|--------------------|
| Person       | `interactions-lead`, `interactions-participant` |
| Organisation | `interactions-sponsor`, `interactions-funder` |
| Community    | `interactions` |
| Project      | `interactions` |

Every element also gets a computed `interactions-all` field: the above
rollup(s) for that type, flattened and deduplicated into one pipe-separated
list, so a single Kumu showcase control works across all node types despite
the field names differing per table (see `kumu-display-settings-internal`).

## Unique IDs

Every element's Kumu ID is `<Type>-<Baserow row id>` (e.g. `Organisation-14`,
`Community-14`). This is what lets same-labelled rows in different tables
(e.g. "OLS" as both an Organisation and a Community) import as distinct Kumu
elements — per Kumu's own duplicate-avoidance rules, once an elements sheet
uses an ID column, connections must reference those IDs (not Labels) in
From/To, which this pipeline does throughout.

## Edge registry (generic types, shared across tables for now)

Only one side of each inverse pair is listed — Baserow link fields exist on
both ends of a relationship, and only one is used to avoid emitting
duplicate edges. Baserow auto-names the "other side" of a link field after
the target table (e.g. plain "People") whenever it hasn't been manually
renamed — that auto-name is still just the inverse of the field it pairs
with, not a separate relationship, and still gets skipped the same way.

| Source table  | Field                              | Target table  | Edge type   |
|---------------|--------------------------------------|---------------|-------------|
| People        | `organisations`                      | Organisations | `employee`  |
| People        | `communities-lead`                   | Communities   | `lead`      |
| People        | `communities-participant`            | Communities   | `participant` |
| People        | `projects-contact`                   | Projects      | `contact`   |
| People        | `projects-lead`                      | Projects      | `lead`      |
| People        | `projects-contributors`              | Projects      | `contributor` |
| Organisations | `communities-sponsor`                | Communities   | `sponsor`   |
| Organisations | `projects-sponsor`                   | Projects      | `sponsor`   |
| Organisations | `projects-funder`                    | Projects      | `funder`    |
| Organisations | `org-child-of`                       | Organisations | `child-of` (self-referencing) |
| Communities   | `organisations`                      | Organisations | `affiliated` ⚠ |
| Communities   | `projects-sponsor`                   | Projects      | `sponsor`   |
| Projects      | `communities`                        | Communities   | `affiliated` ⚠ |

`Communities.people-participants` is the inverse of `People.communities-
participant` — a single relationship, not a second one; skipped like every
other inverse side. Originally auto-named `People` by Baserow (confirmed
2026-09-24); Cass renamed it to `people-participants` (2026-09-25) — same
field id, same relationship, cosmetic rename only. `EXPECTED_COLUMNS`
updated to match so the drift check doesn't flag it.

⚠ **Open question**: `Communities.organisations` and `Projects.communities`
don't have an obvious inverse field on the other side (unlike the
sponsor/funder/lead/contact/contributor pairs above, which mirror a named
field on both tables). They're kept as their own `affiliated` edges rather
than assumed to duplicate the `sponsor` edges already listed — worth
checking once the map is visualised, alongside the still-open
Organisation/Community and Project/other-table boundary questions.

## Fields deliberately not carried into the Kumu export

**People's seven "-user-nominated" fields**, populated by a public
self-nomination form Cass built in Baserow. Their defining property, per the
authoritative policy Cass wrote for the content-extraction skill that writes
to these fields (latest version: the "provenance principle" doc, confirmed
2026-09-24), is *provenance* — a human typed them into that form — not
topic. That policy's write-eligibility rules (what a writer skill may write,
and when it must flag for review) govern a skill that writes to Baserow;
**this pipeline never writes to Baserow at all**, so those specific rules
are Not Applicable to this skill's own behaviour. What does carry over is
the underlying reasoning for why the data is unreliable-until-reviewed,
which is exactly what continues to justify this pipeline excluding all
seven fields from its own (read-only) Kumu export. They split into two
categories with different reasons for exclusion:

**Category A — staging inputs, inherently unreviewed:**
`orgs-user-nominated`, `communities-lead-user-nominated`,
`communities-participant-user-nominated`, `notes-user-nominated`.
These hold exactly what a person typed on the self-nomination form and are
explicitly not meant to be read by anything other than Cass's own manual
review process, which decides whether/how to promote each one into its real
structured field (`organisations` / `communities-lead` /
`communities-participant` / `notes`). **Permanently excluded** from Kumu —
there is no "finished" state for Kumu to read here even in principle; the
finished state is the real field, which this pipeline already reads.

**Category B — real facts, but always flagged for human review:**
`pronouns-user-nominated`, `git-other-user-nominated`,
`socials-other-user-nominated`. Unlike Category A, these ARE the field of
record for a genuine fact that doesn't fit the real field's picklist/format
(e.g. pronouns outside the fixed options). But the policy requires any
write to them to be marked for human review, never silently accepted as
settled — and Baserow currently has **no reviewed-status field** for these
three that this pipeline could check. Excluded from Kumu for now, not
because the data is inherently unusable (unlike Category A), but because
there is currently no signal available to this pipeline distinguishing a
reviewed value from a fresh, unreviewed one.

🔧 **Future development (not yet built)**: if a "reviewed" status field is
ever added to Baserow for the Category B three, this pipeline could safely
include them — gated on that flag — in both exports, subject to the same
consent tier as the rest of a person's profile. Until that field exists,
all seven stay excluded.

`People.edit-row-link` (a Baserow form-view "edit this row" UI helper, not
data) is likewise recognised in `config.EXPECTED_COLUMNS` but never carried
through.

## Consent model (People only)

`mapping-consent` single-select options and how each behaves in the two
exports this pipeline produces:

| Consent value                    | Internal export        | Public export |
|-----------------------------------|-------------------------|----------------|
| `consent-public-identifiable`     | real name, full profile | real name, redacted profile (see below) |
| `consent-public-pseudonymised`    | real name, full profile | hashed label (`Person-xxxxxxxx`), redacted profile |
| `consent-internal`                | real name, full profile | **excluded entirely** |
| `consent-none`                    | real name, full profile | **excluded entirely** |
| `consent-not-asked` / blank       | real name, full profile | **excluded entirely** |

Confirmed by Cass (2026-09-24): this is a deliberate departure from the old
SharePoint-era script, which anonymised but still showed everyone on the
public map. Here, `consent-internal` reads as explicitly not public-safe,
so those people are excluded entirely (element + every edge touching them),
not merely pseudonymised.

The pseudonymised hash is `sha256(salt + kumu_id)[:8]`, stable across runs
(same person always gets the same pseudonym) via a salt file generated once
at `private/kumu/pseudonym-salt.txt` (gitignored, never committed) — not
derivable without that file.

Organisations, Communities, and Projects have no consent field and are
always shown in both exports.

## Profile field redaction on the public export

Two different redaction lists apply to a Person's profile fields on the
**public** export, layered on top of the consent-tier logic above:

**`PERSON_IDENTIFIABLE_FIELDS`** — blanked only for `consent-public-
pseudonymised` people (shown as normal for `consent-public-identifiable`):
`email-1`, `github`, `institutional-profile`, `linkedin`, `ORCID`,
`pronouns`, `carrer-current-role-title`.

**`PERSON_INTERNAL_ONLY_FIELDS`** — blanked for **every** Person on the
public export, regardless of consent tier (including
`consent-public-identifiable`, which the list above doesn't touch):
- `notes` — confirmed by Cass (2026-09-24): free-text notes can carry
  identifying or sensitive detail that a person's consent to appear on the
  public map (even under their real name) doesn't cover.
- `email-2`, `email-3` — confirmed by Cass (2026-09-24): these are likely
  personal (not professional) backup addresses, never the address a person
  would choose to have published. Convention going forward (documented in
  the CRM maintenance notes): `email-1` is reviewed/maintained as the
  primary **professional** email specifically because it's the only one
  ever shown publicly — `email-2`/`email-3` don't need that same scrutiny
  since they never leave the internal export.

🔧 **Future development (not yet built)**: two new People fields are
planned — `mission-interest` and `mission-influence` (naming TBC) — for
mapping a person's interest in / influence over RCM Cooperative's mission.
Confirmed by Cass (2026-09-24): once built, these must go straight into
`PERSON_INTERNAL_ONLY_FIELDS` — never published, at any consent tier. When
added to Baserow: (1) add to `config.EXPECTED_COLUMNS["People"]`, (2) add
to `PROFILE_FIELDS["Person"]` so they're read in at all, (3) add to
`PERSON_INTERNAL_ONLY_FIELDS`.

**Not yet addressed (flagged, not decided)**: relationship/edge fields
(`organisations`, `communities-lead`, `communities-participant`,
`projects-*`, `interactions-lead`/`-participant`) are not filtered by
consent at all right now — a pseudonymised person's connections to
Orgs/Communities/Projects still show up on the map under their pseudonym.
Whether that should also be restricted is a separate, undecided question.

**Currently unredacted at every tier**: `career-stage`,
`communities-contributor-profile`.

## Profile (non-relationship) fields carried onto each element

| Node type    | Fields |
|--------------|--------|
| Person       | `carrer-current-role-title`, `pronouns` (multiselect, pipe-joined), `career-stage`, `notes`, `email-1/2/3`, `github`, `institutional-profile`, `linkedin`, `ORCID`, `communities-contributor-profile` (multiselect, pipe-joined) — redaction per the two lists above |
| Organisation | `type`, `notes`, `website` |
| Community    | `description`, `website` |
| Project      | `description`, `status`, `date-start`, `date-end`, `website` |

Collaborator-name fields (`Created by`, `Last modified by` / `last-modified-by`)
are deliberately never carried onto elements, consistent with existing CRM
skill sanitisation practice.
