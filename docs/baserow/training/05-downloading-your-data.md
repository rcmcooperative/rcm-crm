# Chapter 5: Downloading your data

## Table of contents

- [1. Why you might download your data](#1-why-you-might-download-your-data)
  - [1.1. Compliance warning](#11-compliance-warning)
- [2. How to download your data](#2-how-to-download-your-data)
  - [2.1. Things worth knowing](#21-things-worth-knowing)

---
This chapter describes why and how you might download your data out of Baserow.

---

## 1. Why you might download your data

There are several reasons you might want to download a copy of your data out of Baserow:

1. **Analysis in external tools** — for example, pivot tables or statistics not available natively in Baserow.
2. **Managing mailouts** — there is currently no built-in mailout integration, so exporting a list of email addresses is often the only route to sending a mailout.
3. **Reporting to funders or stakeholders** — for example, a summary shared as Excel or PDF.
4. **Feeding into Kumu** — covered in [Chapter 6: Managing the visualisation](06-managing-the-visualisation.md), but worth naming here as a reason to export.
5. **Sharing a subset of data with a partner organisation** — for example, co-organising an event together. See compliance warning below.
6. **Printing physical materials** — for example, attendee lists or name badges.
7. **Archiving a snapshot** — for example, before a project winds down or a team member leaves.

### 1.1. Compliance warning

Before downloading anything, be confident about where the downloaded data will be stored, so that you remain compliant with your institution's data policy.
A copy sitting in a personal Downloads folder or a personal email account is a much weaker privacy position than the data staying inside Baserow itself.

If you're downloading data specifically to share with a partner organisation (reason 5 above), be aware of the contractual limits this can involve.
Your institution is responsible for holding data about your community — for example, who is on your mailing lists — and it should not be shared with another organisation without a data sharing agreement in place, nor in any way your community might not reasonably expect.

For example, your community would likely expect their contact details to be used to invite them to your own events, but would not necessarily expect those same details to be passed to a third-party printing company in order to produce name badges.

Examples where sharing is highly unlikely to be appropriate:

- Selling or otherwise providing data to a commercial marketing or advertising company.
- Sharing a mailing list with an unrelated research project or organisation, without the individuals' consent.
- Passing a community member's details to their employer, without that person's knowledge or agreement.
- Uploading any part of the dataset to a public or open dataset, without direct opt-in consent.

If in doubt, check with your institution's data protection contact before sharing data outside your own organisation — see also [Data Privacy](01-designing-the-visualisation.md#2-data-privacy) in Chapter 1.

---

## 2. How to download your data

Once your data is populated, you may want to export a copy — either as a backup, or as a structure-only template to share with another community deploying their own RCM-CRM.

**Confirmed navigation path:** `Home` (sidebar) → click the workspace name text itself + its chevron at the top of the Home page — **not** the account-switcher dropdown reached via the small circular initials icon in the sidebar, and **not** a per-database three-dot menu (that one only has Manage members/View API Docs/Rename/Duplicate/Snapshots/View trash/Delete — no Export).

The correct dropdown has: Export data, Import data, Rename workspace, Settings, Members, View trash, Leave workspace, Delete workspace.

**Export data** opens a dialog to select which databases and automations to include, and an `Export structure only` toggle (checked = template-appropriate, no row data; unchecked = includes your actual data, for example, for a backup).

### 2.1. Things worth knowing

- **Automations are not selected by default** in the export dialog — tick them manually, or automations such as the duplicate-detection workflow (Chapter 2's [Dealing with duplicates](02-entering-data.md#8-dealing-with-duplicates) section) won't transfer to an imported copy.
- The exported template `.zip` (structure-only, no automations) is saved in the repo at `assets/baserow-structure/`.
