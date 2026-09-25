# Chapter 3: Maintaining your data

## Table of contents

- [1. Why maintain your data](#1-why-maintain-your-data)
- [2. How to keep records up to date](#2-how-to-keep-records-up-to-date)
  - [2.1. Adding new rows](#21-adding-new-rows)
  - [2.2. Completing fields on an existing row](#22-completing-fields-on-an-existing-row)
  - [2.3. Keeping the Organisations dropdown alphabetical](#23-keeping-the-organisations-dropdown-alphabetical)
  - [2.4. Monitoring and updating email correspondence preferences](#24-monitoring-and-updating-email-correspondence-preferences)
  - [2.5. Reviewing notes-user-nominated submissions](#25-reviewing-notes-user-nominated-submissions)
- [3. How to handle corrections reported outside the self-serve form](#3-how-to-handle-corrections-reported-outside-the-self-serve-form)
- [4. How to respond to data subject requests](#4-how-to-respond-to-data-subject-requests)
- [5. How to review duplicates periodically](#5-how-to-review-duplicates-periodically)
- [6. How to add and review administrators](#6-how-to-add-and-review-administrators)
  - [6.1. Adding administrators](#61-adding-administrators)
  - [6.2. Reviewing administrators](#62-reviewing-administrators)
- [7. How to wind down or archive data](#7-how-to-wind-down-or-archive-data)
- [8. Addendum: proposed development — tracking edit history over time](#8-addendum-proposed-development--tracking-edit-history-over-time)

---

This chapter describes how to maintain your data for accuracy. We start with why you might need to do this, then explain how.

---

## 1. Why maintain your data

It is of high importance to ensure your data are accurate and complete where possible, to reliably understand and communicate with your community. This should be seen as an ongoing responsibility.

Maintenance activity might include:

- Keeping records up to date as your community changes — for example, adding new members when they join your Slack, adding attendees to a new interaction, or adding new organisations your users have provided via the self-serve form (see [`-user-nominated` fields](04-enabling-self-serve-editing.md#121-how-to-add-new-data-into-linked-fields));
- Sharing individual rows with people so they can validate the accuracy of your data holding and consent to be included in the CRM and resulting visualisations, including periodically re-confirming consent rather than treating it as a one-off setting captured at entry;
- Handling corrections reported outside the self-serve form — for example, someone emailing you directly to say their details are wrong, rather than using the Edit row link;
- Responding to data subject requests — someone asking to see what's held about them, correct it, or be removed entirely;
- Ongoing duplicate review — a periodic sweep, not just catching duplicates as they're entered;
- Periodically reviewing who has editor or admin access to the workspace, especially as people join or leave the team;
- Monitoring and updating email correspondence preferences — keeping `email-1` as each person's primary professional email, with `email-2` and `email-3` kept only as backups (see [Monitoring and updating email correspondence preferences](#24-monitoring-and-updating-email-correspondence-preferences));
- Reviewing `notes-user-nominated` submissions and deciding, case by case, whether anything in them is worth carrying into the internal notes field (see [Reviewing notes-user-nominated submissions](#25-reviewing-notes-user-nominated-submissions));
- Keeping regular backups — see [Chapter 5: Downloading your data](05-downloading-your-data.md), which also serves as a maintenance safeguard, not just a one-off export;
- Deciding what happens to the data if a project ends, someone leaves, or the community itself stops being active.

---

## 2. How to keep records up to date

Keeping records up to date splits into several kinds of task:

### 2.1. Adding new rows

When someone or something new joins your community — for example:

- A review of your mailing list or Slack members, adding anyone new as a Person row;
- A new interaction (event, meeting, conversation) adds new participant links, and possibly new People, Organisation, or Project rows if any of those are new to the CRM;
- New organisations or communities nominated by users via the sign-up/edit form (see [`-user-nominated` fields](04-enabling-self-serve-editing.md#121-how-to-add-new-data-into-linked-fields)). These submissions are only free text at the point of submission — they don't automatically become real, linked `Organisations` or `Communities` rows. You'll need to periodically process these manually: create the proper row for each new organisation or community named, link it to the person who nominated it, and re-sort the relevant table alphabetically (see [Keeping the Organisations dropdown alphabetical](#23-keeping-the-organisations-dropdown-alphabetical)) so it appears in alphabetical order the next time the form is used.

Adding new rows for these cases is done using the same two methods covered in Chapter 2 — copy/paste via the [Grid view](02-entering-data.md#72-add-via-grid-view), or the [enlarged row view](02-entering-data.md#73-add-data-by-enlarged-row) for a single row. <mark>Baserow also has a native import function (for example, importing a CSV of new mailing list members directly), which will be explored in a future development.</mark>

### 2.2. Completing fields on an existing row

When you learn more about someone or something already in the CRM — for example:

- Adding a missing email address once you have it;
- Linking a person to a new organisation or project once that link becomes relevant;
- Filling in a field that was left blank at first entry.

These tasks are performed using the method described in Chapter 2's [Add data rows](02-entering-data.md#7-add-data-rows) section — the difference here is treating it as an ongoing, recurring task (for example, a monthly review) rather than only a one-off bulk entry when you first set up the CRM.

**A note on what we've deliberately not built:** it would be technically possible to automatically fill in missing fields — for example, looking up someone's Open Researcher and Contributor ID (ORCID) or institutional web profile automatically online — since this kind of information is often publicly available. We've deliberately not built a skill to do this. Even though the data is public, automatically compiling it about someone without asking is a different act from a person looking it up manually when needed, and we think it's the responsible approach to check with our own community first — and be transparent about the process — before doing this ourselves or sharing a method to do it with others. <mark>Revisit when this has been discussed with the community.</mark>

### 2.3. Keeping the Organisations dropdown alphabetical

If your `Organisations` table is offered as a dropdown on a public form (see [Enabling self-serve editing](04-enabling-self-serve-editing.md)), be aware that Baserow orders a link field's dropdown by the unsorted row order as they appear in the source table, not by any sort or filter applied to a view. Applying an alphabetical sort to the `Organisations` table's view does **not** change the order items appear in the form dropdown.

To keep the dropdown alphabetical, you need to manually drag-and-drop the rows into alphabetical order in the `Organisations` table's Grid view. Start by turning off all sorting on the view (see [Review sorting and filtering options](02-entering-data.md#61-review-sorting-and-filtering-options)), then click and drag rows into alphabetical order by hand. This is a genuine ongoing task: each time a new organisation is added, it will need to be manually dragged into its correct alphabetical position, rather than simply appearing at the bottom of the list. <mark>No native way to automate this currently exists in Baserow.</mark>

### 2.4. Monitoring and updating email correspondence preferences

The `People` table holds up to three email fields — `email-1`, `email-2`, and `email-3`. Treat these consistently, rather than as three interchangeable places to put whatever address you happen to have:

- `email-1` — the person's **primary professional email**. This is the address correspondence (for example, mail merges distributing [Edit row links](04-enabling-self-serve-editing.md#132-users-link) — see Chapter 4) should be built against by default.
- `email-2` and `email-3` — **backups only**, for example a personal address kept on file in case the primary becomes unreachable or changes. These shouldn't be used for routine correspondence.

As part of your periodic review (see [How to keep records up to date](#2-how-to-keep-records-up-to-date)), check that:

- `email-1` is still current, and still the address the person would want used;
- if someone tells you their professional email has changed, the old address moves into `email-2` or `email-3` rather than being overwritten outright — so it stays on file as a backup route to reach them if needed;
- any correspondence you're preparing (for example, a mail merge) is built against `email-1`, not `email-2`/`email-3`.

<mark>This is a manual convention to apply when entering or reviewing data — Baserow has no native way to enforce which of the three fields is treated as primary.</mark>

### 2.5. Reviewing notes-user-nominated submissions

`notes-user-nominated` (see [`-user-nominated` fields](04-enabling-self-serve-editing.md#121-how-to-add-new-data-into-linked-fields) in Chapter 4) is a free-text field on the sign-up/edit form, prompting the person with "anything else you'd like us to know" — for example their interests, expertise, or career aspirations. Unlike `orgs-user-nominated` or `communities-lead-user-nominated`, there's no linked table to turn this into: it's just text, submitted directly.

Because it's exposed on the edit form, `notes-user-nominated` is also something the person can come back and overwrite — updating or clearing what they wrote the next time they use their Edit row link (see [Editing existing rows via the form](04-enabling-self-serve-editing.md#13-editing-existing-rows-via-the-form)). That makes it a genuinely transient field, not a durable record: whatever's useful in it can be lost the next time the person edits their own row, unless you've deliberately preserved it elsewhere.

**Review periodically** (as part of the same pass as [How to keep records up to date](#2-how-to-keep-records-up-to-date)):

1. Read each new or changed `notes-user-nominated` entry.
2. Decide, case by case, whether anything in it is worth carrying into the internal notes field — for example, something that helps you tailor offerings to that person or connect them with the right people, and that you'd want kept even if they later change or delete what they wrote.
3. If so, copy the relevant part across yourself. There's no automatic sync between the two — `notes-user-nominated` stays as the person's own, self-serve-editable text; the internal notes field is the durable, administrator-maintained record.

<mark>Confirm which field on the People table is the intended destination for this (for example, whether this should be the same field the `crm-notes-extraction` skill writes to, or a separate one) — not yet settled in this documentation.</mark>

---

## 3. How to handle corrections reported outside the self-serve form

Not every correction comes in through the self-serve form — someone may simply email you directly to say their details are wrong, or mention it in conversation.

There's no special process for this: find the row (for example, using the `Enlarge row` → `Copy row URL` route in [Editing existing rows via the form](04-enabling-self-serve-editing.md#13-editing-existing-rows-via-the-form), or by searching/filtering the table directly) and edit it using any of the methods already covered in [How to keep records up to date](#2-how-to-keep-records-up-to-date) — typically the enlarged row view for a single correction.

The only thing worth doing differently here is a brief acknowledgement back to the person once it's fixed, since — unlike a self-serve submission — they have no way of knowing whether their email was seen or acted on.

## 4. How to respond to data subject requests

A data subject request is when someone asks what personal data you hold about them, asks you to correct it, or asks for it to be deleted entirely. These are legal rights under data protection law (for example, UK/EU GDPR), not just a courtesy — see [Data Privacy](01-designing-the-visualisation.md#2-data-privacy) in Chapter 1, and your institution's Data Privacy (Impact) Assessment, for the legal obligations and response timeframes that apply to your organisation. <mark>This section covers the practical CRM mechanics only — check with your institution's data protection contact for the legal requirements (response deadlines, identity verification standards) that apply to you.</mark>

**Verify who's asking, before acting.** Anyone can email claiming to be someone in your database — confirm the request is genuinely coming from the person concerned (for example, from the email address already on file) before making any change.

**Access requests** ("what do you hold about me?"): find their row (see [Editing existing rows via the form](04-enabling-self-serve-editing.md#13-editing-existing-rows-via-the-form) for locating a row via `Copy row URL`), and share the relevant field values back to them directly — there's no need to give them raw database access.

**Rectification requests** (correcting inaccurate data): handled the same way as any other correction — see [How to handle corrections reported outside the self-serve form](#3-how-to-handle-corrections-reported-outside-the-self-serve-form) above.

**Erasure requests** (deleting their data entirely): delete their row from the relevant table(s).

What happens to linked records is only partly confirmed. Baserow's own documentation confirms that deleting a whole **table** leaves link fields elsewhere referencing it "broken" and showing empty values, rather than a visibly dangling reference — but there's no equivalent documented confirmation for deleting a single **row** specifically. Deleted rows go through a trash/grace period before permanent deletion, and one point worth being aware of: an older Baserow development note flagged that a deleted row's disappearance from a linked table's display wasn't always pushed in real time to other people already viewing that table. <mark>Confirm this behaviour directly (does an Interaction or Project row that was linked to a deleted Person show a broken/empty link, and does this happen immediately or only after a refresh/the trash grace period) before relying on it for a real erasure request.</mark>

**Keep a record that the request was handled** (who asked, what was done, and when) — for your own accountability — without storing any more personal detail about the request than necessary.

**Preventing re-addition after erasure.** A record that a request was handled (above) doesn't by itself stop the person being re-added later — by a different administrator, a future mailing-list or Slack member review, or an automated import — since nothing currently checks new entries against it.

Consider maintaining a separate, minimal **suppression list**: just enough to recognise the person again (for example, name and email), stripped of everything else, checked against before adding any new row from a mailing list, Slack review, or similar. Retaining this minimal record is generally a recognised exception to an erasure request, since it exists specifically to honour that request going forward, not to hold onto their data — but confirm this reasoning with your institution's data protection contact rather than relying on this documentation alone.

<mark>Not yet built: no suppression-list mechanism or check currently exists in the CRM or its skills (`crm-notes-extraction`, `crm-email-contacts`, or manual entry). Marked for future development.</mark>

## 5. How to review duplicates periodically

The mechanics of finding and resolving duplicates are covered in Chapter 2's [Dealing with duplicates](02-entering-data.md#8-dealing-with-duplicates) section. This section is about doing that as an ongoing habit, not only when entering new data.

**Suggested cadence:** monthly, or whenever a batch of new data has been added (for example, after processing a set of `-user-nominated` submissions, or importing a new mailing list/Slack member review). Duplicates are most likely to appear right after a bulk addition, so tying the check to those moments catches more of them than a fixed calendar date would on its own.

**What to check:** repeat the manual sort-and-scan process (Chapter 2, [Dealing with duplicates](02-entering-data.md#8-dealing-with-duplicates)) across all five tables — `People`, `Organisations`, `Communities`, `Interactions`, `Projects` — not just `People`, since the same risk (the same real-world entity entered twice) applies to any of them.

This is a natural point to combine with two other periodic tasks that touch the same tables: [Keeping the Organisations dropdown alphabetical](#23-keeping-the-organisations-dropdown-alphabetical), and turning `-user-nominated` free-text submissions into proper rows (see [Adding new rows](#21-adding-new-rows)) — doing all three together as one monthly pass is more efficient than treating them as separate, differently-timed chores.

<mark>Marked for future development: build a checklist of maintenance tasks, split into periodic (for example, monthly) and activity-triggered (for example, after a bulk import) categories, so these don't rely on being remembered individually across this chapter. This checklist should include a cadence for re-confirming consent, to be discussed with your data protection contact.</mark>

## 6. How to add and review administrators

### 6.1. Adding administrators

New collaborators are added at workspace level, via email invitation, with a role assigned at the point of inviting. See the **Baserow docs:** [Add workspace collaborators](https://baserow.io/user-docs/working-with-collaborators) page for the full walkthrough.

Baserow's free plan offers basic roles (for example, Admin, Member); Advanced/Enterprise plans add more granular role-based access control, down to database and table level. See the **Baserow docs:** [Permissions overview](https://baserow.io/user-docs/permissions-overview) page for the full comparison, and the **Baserow docs:** [Assign roles to members at workspace level](https://baserow.io/user-docs/assign-roles-to-members-at-workspace-level) page for how roles work in practice.

**Maintain at least two workspace admins.** A single admin leaving or losing access can otherwise leave the whole workspace unmanageable — see the **Baserow docs:** [Manage workspace members](https://baserow.io/user-docs/manage-workspace-permissions) page.

### 6.2. Reviewing administrators

Periodically review who has access and at what level — Baserow's own documentation recommends this specifically after a project concludes, when a team member's role changes, or when an external collaborator's work ends. See the **Baserow docs:** [Manage workspace members](https://baserow.io/user-docs/manage-workspace-permissions) page for viewing the current member list and changing roles.

**Removing access:** removing someone from the workspace (via the Members page) revokes their access to that specific workspace, but they can still log into Baserow and access any other workspace they belong to — this is different from deleting their user account entirely, which is a separate, more drastic action. See the **Baserow docs:** [Manage workspace members](https://baserow.io/user-docs/manage-workspace-permissions) page for how to do this.

## 7. How to wind down or archive data

Winding down might mean the whole CRM stops being used (the community or project ends), or something narrower (a single team member with admin access leaves, one community within the CRM stops being active). What to do depends on which of these applies, and the decision itself is more of an institutional/policy question than a Baserow mechanic — this section covers the practical steps, not the decision of whether to retain or delete.

<mark>Check with your institution's data protection contact before winding down: the consent your community gave (see [Data Privacy](01-designing-the-visualisation.md#2-data-privacy) in Chapter 1) was likely given in the context of an active, ongoing community — winding down may itself be something you need to notify people about, or a trigger to re-confirm whether they're still happy for their data to be held.</mark>

**If a single admin leaves:** see [How to add and review administrators](#6-how-to-add-and-review-administrators) — this is a routine access review, not a data wind-down.

**If a single community, project, or organisation stops being active:** there's no need to delete anything — just leave the existing rows as historical record, and stop adding new interactions/data for that community going forward. The data remains useful for understanding your community's history even once a specific thread within it is inactive.

**If the whole CRM is winding down:**

1.  **Take a final archived export** (see [Chapter 5: Downloading your data](05-downloading-your-data.md)) — this is your only copy once the live workspace is gone.
2.  **Decide what happens to the live Baserow workspace** — delete it, leave it dormant (still costing nothing on the Free plan, but still holding live personal data), or transfer ownership to someone else at your institution.
3.  **Decide what happens to any published Kumu visualisation** (see Chapter 6) — this is public-facing, so unpublishing or deleting it is likely to need to happen alongside, not after, any decision to delete the underlying data.
4.  **Decide what happens to the archived export itself** — how long it's retained, where it's stored, and who else (if anyone) can access it — the same institutional storage/compliance considerations as any other download (see [Chapter 5: Downloading your data](05-downloading-your-data.md#11-compliance-warning)).

## 8. Addendum: proposed development — tracking edit history over time

As noted in [Chapter 4: Enabling self-serve editing](04-enabling-self-serve-editing.md), Baserow doesn't currently show a modification history or diff for edits made via the Edit row link, and the `Last modified by` field isn't a durable record of a self-serve edit — it gets overwritten as soon as anyone else edits the same row.

<mark>This section is a proposal for a future development, not yet built.</mark>

**The core mechanic: snapshot and diff on Row ID.** Row IDs are permanent and never reused, which makes them a clean, stable join key across time points — no extra tracking column is needed to know "this is the same real-world row" from one export to the next.

The process would look something like:

1.  **Take periodic exports** of each table (`People`, `Organisations`, `Communities`, `Interactions`, `Projects`), on some interval — weekly or monthly. This could reuse the existing read-only-token API approach already used for schema extraction, or just Baserow's per-table CSV/JSON export. Save each into a dated folder, mirroring the existing `assets/baserow-structure/structure-exports/YYYY-MM-DD/` convention already used for schema snapshots.
2.  **Match rows across two consecutive snapshots by Row ID.** For each table, compare snapshot N against snapshot N-1:
    - Row ID in N but not N-1 → new row.
    - Row ID in N-1 but not N → deleted row.
    - Row ID in both, but any field value differs → modified row.
3.  **For modified rows, diff field-by-field** and record what changed — old value, new value, and which field. Rows could be narrowed first by checking each row's `Last modified` timestamp against the previous snapshot's export date, and only doing a full field-by-field diff on rows with a newer timestamp — though at CRM scale, just diffing every row each time might be simpler and fast enough not to bother optimising.
4.  **Accumulate results into one long-format change log**, rather than a separate diff file per snapshot pair — for example, `snapshot_date, table, row_id, field, old_value, new_value`. This is the useful long-term artefact, not the individual snapshots themselves.

**Visualising it in Excel:**

- **A single "Change log" sheet**, in the long/tidy format above, formatted as an Excel Table so it's filterable and sortable out of the box — by date range, table, field, or a specific row/person.
- **A pivot table off that log**, for summary views — for example, count of changes per person over time (who's actively keeping their data current versus who never touches it), or count of changes per field (which fields get corrected most often — a possible signal that a field's original data entry, or a dropdown option, needs fixing).
- **A pivoted "what changed" view**, if a friendlier read than the raw log is wanted: one row per person, one old/new column pair per field, changed cells highlighted. More work to build than the log itself, so a nice-to-have layered on top rather than the core deliverable.

**Open question for when this becomes a real project:** whether the snapshot exports themselves get kept indefinitely (a full historical archive) or whether only the derived change log is kept long-term and the raw snapshots get pruned after each diff — a storage and privacy trade-off, given this is personal data about the community, not just a technical one.
