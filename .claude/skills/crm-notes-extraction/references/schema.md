# RCM Cooperative CRM Schema (Baserow)

Five tables, rebuilt against the actual live Baserow structure (confirmed via the read-only field-definitions API export, Sept 2026 — not a plan or a guess). Column names below are exact — copy them verbatim into the output CSV. Do not rename, reorder, or invent columns.

**Source material**: `docs/baserow-structure/baserow-structure-json-<Table>.json` at the repo root holds the raw field-definitions API export per table (formula text, select options, field types) that this schema and `scripts/build_workbook.py` were built from — kept there for audit/reference, not read by this skill at runtime.

**Column order is deliberately not tracked.** An earlier version of this skill tried to make the output xlsx's column order match Baserow's live on-screen order exactly, so a full row-range could be pasted straight across with no realignment. That required manually screenshotting Baserow's "Hide columns" panel per table, and it proved fragile — the order drifted out of sync more than once, and pinning it down worked against the flexibility of anyone templating their own instance from this one and reordering fields to suit themselves. That approach has been dropped. The output xlsx now lists each table's writable columns in a fixed, sensible order of its own (see `ALL_HEADERS` in `build_workbook.py`) that has no relationship to Baserow's on-screen order. **Practical consequence**: importing a table's sheet into Baserow now means matching columns by header name rather than pasting a whole row range in one go — slower per import, but never silently misaligned. A proper fix (Baserow's own import feature, which matches by field name automatically) is planned for a future release; this is the interim approach until then.

**Formula syntax note**: every formula on this platform uses Baserow's own syntax — `field('Column Name')` (single quotes, function call, not curly braces) and `concat(...)`/`isblank(...)` for string joining and blank-checks. This is different from the SeaTable syntax this schema used before the platform migration.

## People

`name-person` (formula), `name-person-first`, `name-person-last`, `email-1`, `email-2`, `email-3`, `carrer-current-role-title`, `organisations`, `communities-contributor-profile`, `communities-lead`, `communities-participant`, `interactions-lead`, `interactions-participant`, `pronouns`, `pronouns-user-nominated`, `notes`, `github`, `git-other-user-nominated`, `institutional-profile`, `linkedin`, `socials-other-user-nominated`, `ORCID`, `projects-contact`, `projects-lead`, `projects-contributors`, `career-stage`, `mapping-consent`, `Last modified`, `Last modified by`

Fields the skill must **never** write to (staging inputs for a separate self-nomination-form pipeline, or system/formula fields): `name-person`, `Last modified`, `Last modified by`, `Created on`, `Created by`, `edit-row-link`, `orgs-user-nominated`, `communities-lead-user-nominated`, `communities-participant-user-nominated`, `notes-user-nominated`.

Notes:
- `name-person` is an **auto-computed formula column**: `field('name-person-first')+ " " + field('name-person-last')`. Never write to it directly — populate `name-person-first` and `name-person-last` instead.
- `carrer-current-role-title` — yes, that's the real spelling in the live base (typo: "carrer"). Copy it exactly.
- `email-3` — plain text, same treatment as `email-1`/`email-2`.
- `organisations` — Link to Organisations. The real, only affiliation link — populate as a link when the organisation already/will exist as a row.
- `communities-contributor-profile` — **multiple select**. Confirmed options: `communications`, `engagement`, `project-management`, `technical`, `strategy`. General contributor-profile competency, gathered once per person, not scoped per community.
- `communities-participant` — **Link to table** (Communities). A person's participation in a specific community (distinct from `communities-lead`, which is leadership specifically, and from `communities-contributor-profile`, which is a general competency-area tag not scoped to any one community). Populate when notes clearly show someone participating in a named community, not merely mentioned in passing. Baserow auto-generates a matching reverse field on Communities (`people-participants`) — this skill never writes to that reverse field directly; Baserow keeps both sides in sync automatically.
- `communities-lead` / `interactions-lead` / `interactions-participant` / `projects-contact` / `projects-lead` / `projects-contributors` — Link to table fields.
- `pronouns` — **multiple select**. Confirmed options: `she/her`, `he/him`, `she/they`, `they/she`, `they/them`, `he/they`, `they/he`, `self identify`.
- `github` — GitHub username/URL specifically.
- `linkedin` — LinkedIn URL specifically.
- `career-stage` — single select. Confirmed options (reworded, Sept 2026): `Undergraduate student`, `Graduate Student`, `Early Career`, `Mid Career`, `Project Lead`, `Director`. (Old→new mapping, for reference only — always use the new strings: undergrad→Undergraduate student, grad-student→Graduate Student, ecr→Early Career, senior→Mid Career, pi→Project Lead, director→Director.)
- `mapping-consent` — single select. Confirmed options: `consent-not-asked` (default), `consent-none`, `consent-internal`, `consent-public-pseudonymised`, `consent-public-identifiable`.
- `notes`: interest-area/background only — never what the meeting discussed.
- `Last modified` / `Last modified by` / `Created on` / `Created by` — Baserow system fields (auto-tracked, read-only). Never write to these. Note the capitalisation/spacing here doesn't match the `last-modified-by`/`last-modified-date` convention used on the other four tables — a naming inconsistency that's been flagged but not yet fixed.
- Only add a row for someone directly present at a meeting (attendee, or a named apology). See SKILL.md Step 1 for the one exception (quoted speakers when the attendee list is unreadable, which must be flagged/resolved with Cass first).

### The seven `*-user-nominated` fields — provenance principle

These fields exist because Cass built a **self-nomination/signup form** in Baserow, where people submit information about themselves directly. **The defining property of every `*-user-nominated` field is provenance, not topic**: it holds what a human typed about themselves through that form. A fact that happens to be topically similar — e.g. an organisation inferred from an email domain, or a role inferred from a Slack message — is still machine-derived, not a person's self-report, and provenance is what decides write eligibility here, not subject-matter overlap. No automated process should ever write to a `*-user-nominated` field on the strength of "this looks like the kind of thing that goes here" — only an actual human-submitted-form value belongs there.

> **Not applicable to this skill in practice, but stated for consistency with sibling skills**: this skill only ever extracts from human-authored meeting notes, and its core rule ("No inference beyond the text — only from what the notes state," see Cross-cutting conventions below) already excludes machine-derived signals by construction. There is no email-domain, activity-log, or algorithmic-guess data source anywhere in this skill's pipeline for the provenance principle to actively guard against. It matters more for sibling skills that *do* process machine-derived signals (e.g. an email-thread extraction skill inferring an organisation from a sender's email domain) — this section is written to be copied into those skills' schema docs verbatim, so the principle stays consistent everywhere it applies.

**Category A — staging inputs, never write to these:** `orgs-user-nominated`, `communities-lead-user-nominated`, `communities-participant-user-nominated`, `notes-user-nominated`.

These hold what a person typed on the self-nomination form, as free text — a claimed organisation, a claimed community-leadership role, a claimed community-participation, or general notes. They are not meant to be filled by anything else, human-authored or machine-derived. Cass manually reviews each one and decides whether/how to convert it into the real structured field (`organisations`, `communities-lead`, `communities-participant`, or folded into `notes`). This skill is a different pipeline entirely — never write to any of these four fields, even if the notes state exactly the kind of information they hold, and even when the extracted value is confidently correct. If a meeting note says "Sara said she leads the CSCCE community," that's a candidate for the real `communities-lead` link field (subject to normal node-reconciliation rules) — not for `communities-lead-user-nominated`, which is reserved for what the person themselves typed into the form.

**Category B — flexibility overflow, writable with a mandatory review flag:** `pronouns-user-nominated`, `git-other-user-nominated`, `socials-other-user-nominated`.

These exist to capture a real, useful fact that doesn't fit a fixed field or picklist — not staging for a separate pipeline. This skill **should** write to these when the notes state the relevant fact, following the per-field rules below, and must always mark the write for human review (never silently accept it as settled — see `EXPLICIT_FLAG_COLUMNS` in `build_workbook.py`):

- `pronouns-user-nominated` (plain text) — the notes state pronouns that don't match any option in the `pronouns` picklist (`she/her`, `he/him`, `she/they`, `they/she`, `they/them`, `he/they`, `they/he`, `self identify`). Write the stated pronouns here verbatim as free text. Never write both `pronouns` and `pronouns-user-nominated` for the same fact.
- `git-other-user-nominated` (long text) — the notes mention a username on a git-hosting platform **other than GitHub** (e.g. "prefers to use codeberg: @username"). Write it as a full URL where possible (e.g. `www.codeberg.org/username`), not just the bare username.
- `socials-other-user-nominated` (long text) — the notes mention a username on a social network **other than LinkedIn** (e.g. "regularly active on bluesky, @username"). Write it as a full URL where possible (e.g. `www.bluesky.org/username`), not just the bare username.

Category B is still bounded by the provenance principle above: what makes these writable is that the notes themselves are reporting a fact the person stated (a pronoun the notes record someone giving, a handle someone mentioned) — the skill is transcribing a stated fact into an overflow slot, not inventing or inferring one.

**One more, non-writable either way:** `edit-row-link` — a read-only Baserow system field tied to a form view. No skill ever writes to this.

**Summary rule of thumb for other skills reusing this schema**: ask provenance first, then shape. If the value did not come from the person's own self-report — it was derived, inferred, or extracted by code from some other fact (an email domain, an activity log, an algorithm's guess) — it never goes into a `*-user-nominated` field, full stop, regardless of how well its topic matches. Only once a value is confirmed as a genuine human self-report does the second question apply: if the field name pairs with a link field that already has its own clean write target elsewhere in the schema (Category A) — forbidden, stays staged for Cass's manual review. If it pairs with a scalar field where the fixed field/format genuinely can't hold what the source says (Category B) — writable, always flagged.

## Organisations

`name-org` (formula), `people-employees`, `type`, `name-org-long`, `name-org-abbreviation`, `notes`, `website`, `communities-sponsor`, `projects-sponsor`, `projects-funder`, `interactions-sponsor`, `interactions-funder`, `last-modified-by`, `last-modified-date`

Fields the skill must **never** write to: `name-org`, `last-modified-by`, `last-modified-date`, `Created on`, `Created by`, `org-child-of`.

Notes:
- `name-org` is an **auto-computed formula column**: `if(isblank(field('name-org-abbreviation')), field('name-org-long'), concat(field('name-org-long'), ' (', field('name-org-abbreviation'), ')'))`. Populate `name-org-long` (always) and `name-org-abbreviation` (only if given) instead.
- `type` (single select). **Exact picklist, use one of these only:**
  - `Academic institute` — a university or dedicated research body engaged in teaching and/or research.
  - `Consortium` — specifically an *academic* consortium.
  - `Public sector / Government` — a national, regional, or local government body or agency.
  - `Private industry` — a for-profit commercial company.
  - `Non-profit` — an organisation not distributing profit to owners/shareholders.
  - `Funder` — an organisation whose primary role in the relationship is providing grant or programme funding.
  - `Intergovernmental organisation` — a body formed by and representing multiple national governments.
  - `Cooperative` — a member-owned organisation with democratic one-member-one-vote governance.
  - `Social enterprise` — a revenue-generating business whose profits are reinvested toward a social/environmental mission.
  - If you cannot determine the type from the notes alone, leave blank and flag. Do not look it up online.
- `people-employees` — Link to People. The only People-link field on Organisations.
- `communities-sponsor` / `projects-sponsor` / `projects-funder` / `interactions-sponsor` / `interactions-funder` — Link fields. Sponsor and funder are two distinct relationship types. If the notes don't clearly distinguish, flag rather than guessing.
- **`org-child-of`** — self-referencing Link field (parent/child organisation relationship). **This skill must never write to it.** Confirmed with Cass: these parent-child relationships are rarely stated directly in meeting notes — they're mostly tacit knowledge — so this is Baserow-manual-entry only, not something to extract or infer.
- Only add the **primary** organisation(s) actually under discussion.
- `last-modified-by` / `last-modified-date` / `Created on` / `Created by` — Baserow system fields (read-only). Never write to these.

## Communities

`name-community` (formula), `description`, `name-community-long`, `name-community-abbreviation`, `people-leads`, `website`, `organisations`, `projects-sponsor`, `interactions`, `last-modified-by`, `last-modified-date`

Notes:
- `name-community` is an **auto-computed formula column**, same pattern as `name-org`. Populate `name-community-long` (always) and `name-community-abbreviation` (only if given) instead.
- Can be added whenever mentioned, even if not the primary topic of the meeting.
- `people-leads` — Link to People (leadership specifically).
- `people-participants` (informational only — do not write to this) — Baserow's auto-generated reverse-link field, paired with People's `communities-participant`. Confirmed correctly renamed in Baserow (was the unhelpful default `"People"`, now `people-participants`, matching the `people-employees` naming convention used on Organisations). Baserow keeps this in sync automatically whenever `communities-participant` is set from the People side — this skill never writes to it directly.
- `description` and `website` are genuine fields on this table. There is **no `outputs`, `geographic-scope`, or `maturation-stage` field**. If notes describe any of these concepts, put them in `description` as free text.
- `organisations` — Link to Organisations (a Community can link to more than one).
- `projects-sponsor` — Link to Projects.
- `interactions` — Link to Interactions. **Note the exact name: `interactions`, not `interactions-sponsor`.** This is a plain association (a Community that was involved in a given Interaction) — there is no sponsor/funder distinction on this particular relationship, unlike Organisations' link to Interactions, which does have that distinction.
- Node-reconciliation: don't create an Organisations row AND a Communities row for the same name unless there's a real, fillable relationship-shape in both.

## Projects

`name-project` (formula), `description`, `date-start`, `date-end`, `status`, `interactions`, `people-contacts`, `name-project-long`, `name-project-abbreviation`, `people-leads`, `people-contributors`, `github-issue`, `notes`, `org-sponsor`, `org-funder`, `communities`, `website`, `last-modified-by`, `last-modified-date`

No changes this update — confirmed unchanged against the newest export.

Notes:
- `name-project` is an **auto-computed formula column**, same pattern as `name-org`.
- `status` (single select). **Exact picklist for Projects — NOT the same list as Interactions:** `planned`, `ongoing`, `completed`, `paused`.
- `org-sponsor` / `org-funder` — two distinct Link-to-Organisations fields.
- `communities` — Link to Communities (plural).
- `interactions` — Link to Interactions.
- `people-contacts` / `people-leads` / `people-contributors` — Link to People, three distinct roles.
- `github-issue` — URL, only if the notes give one directly.
- Only add the **primary** project(s) actually under discussion.
- `last-modified-by` / `last-modified-date` — Baserow system fields (read-only). Never write to these.

## Interactions

`name-interaction` (formula), `status`, `date-started`, `notes`, `people-leads`, `projects`, `people-participants`, `name-interaction-long`, `name-interaction-abbreviation`, `type`, `urls-outputs`, `urls-internal`, `date-delivered`, `date-last-activity`, `github-issue`, `communities`, `org-sponsor`, `org-funder`, `last-modified-date`, `last-modified-by`

Fields the skill must **never** write to: `name-interaction`, `last-modified-date`, `last-modified-by`, `Created on`, `Created by`.

Notes:
- `name-interaction` is an **auto-computed formula column**, same pattern as `name-org`.
- `status` (single select). **Exact picklist for Interactions — NOT the same list as Projects:** `pre-submission / planned`, `submitted / under-review`, `active / confirmed`, `completed`, `rejected`, `paused`.
- `type` (single select). Confirmed options (updated Sept 2026): `meeting`, `call-series`, `presentation`, `email-only`, `slack-channel`, `conference`, `seminar`. Note `slack-only` was deliberately renamed to `slack-channel` — the `-only` suffix convention no longer applies uniformly going forward (`conference`/`seminar` were added without it), so don't assume future single-channel types will follow an `-only`/`-channel` pattern; use whatever the live picklist actually shows. If a project/relationship already has a live meeting cadence (`meeting` or `call-series`), don't create a separate email/slack/etc. interaction row for it — summarise that activity in `notes` instead.
- **One Interactions row per notes file, not per dated meeting section within it.** See SKILL.md Step 1.
- `urls-outputs` / `urls-internal` — plain **Text** fields, not URL type. Free text, potentially multiple URLs.
- `org-sponsor` / `org-funder` — two distinct Link-to-Organisations fields.
- `communities` — Link to Communities.
- `date-started`: earliest meeting date across all dated sections in the file.
- `date-last-activity`: most recent meeting date across all dated sections in the file.
- `date-delivered`: only set if the notes clearly indicate the engagement has concluded.
- `last-modified-by` / `last-modified-date` / `Created on` / `Created by` — Baserow system fields (read-only). Never write to these.

## Cross-cutting conventions

- **Scope**: only interactions run by RCM Cooperative's own community are recorded.
- **Flagging**: any fact you couldn't determine directly from the notes should simply not be written as a line in the candidates CSV — an omitted field is automatically flagged in the output. The three `*-user-nominated` overflow fields (`pronouns-`, `git-other-`, `socials-other-`) additionally get an **explicit** flag when written (per their per-table notes above) — since these represent a genuine ambiguity worth a human glance (does this really not fit the fixed picklist / real field?), not just a missing fact.
- **No inference beyond the text.** Don't infer an organisation's legal form, a person's affiliation, or a project's status from general knowledge — only from what the notes state.
- **Formula and system columns — never write to these directly, on any table:**
  - Formula (auto-computed display names): `name-person` (People), `name-org` (Organisations), `name-community` (Communities), `name-project` (Projects), `name-interaction` (Interactions).
  - System/read-only (auto-tracked by Baserow): `Last modified` / `Last modified by` / `Created on` / `Created by` (People), `last-modified-by` / `last-modified-date` / `Created on` / `Created by` (all other four tables — note Communities does not currently have `Created on`/`Created by` fields, unlike the other three).
- **Staging/self-nomination-form fields (People only) — never write to these:** `orgs-user-nominated`, `communities-lead-user-nominated`, `communities-participant-user-nominated`, `notes-user-nominated`, `edit-row-link`. These belong to a separate signup-form pipeline that Cass reviews manually; meeting-notes extraction is not that pipeline.
- **Manual-only relationship fields — never write to these:** `org-child-of` (Organisations) — parent/child org relationships are tacit knowledge, not something stated in notes.
- **Auto-generated reverse-link fields — never write to these:** `people-participants` (Communities) — Baserow keeps this in sync from the People-side `communities-participant` field automatically.
- **Sponsor vs Funder** appears on Organisations↔Projects and Organisations↔Interactions specifically. Communities↔Interactions and Communities↔Projects are plain associations with no sponsor/funder distinction.
</content>
