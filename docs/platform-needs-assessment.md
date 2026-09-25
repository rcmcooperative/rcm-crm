# Platform needs assessment: RCM-CRM data infrastructure

This document records why RCM Cooperative assessed several platform options for hosting RCM-CRM data, and what it decided.
Use this document for internal reference, or hand it to an external reviewer, such as an IT team or a Data Privacy Officer, assessing whether a given platform is appropriate for a deployment.

## Why this assessment exists

The original RCM-CRM architecture assumes self-hosting by default: a Docker-based application connecting to a local SQLite or Postgres database, with no data leaving RCM Cooperative's, or a client's, own infrastructure.
This design remains the strongest option on data privacy: no third-party processor is involved at all.
See `self-hosted-architecture/` for the full design; the RCM Cooperative's own CRM is now built on Baserow instead, described in `baserow/architecture-overview.md` and `baserow/schema.md`.

Three further requirements led RCM Cooperative to assess platforms beyond this design for some deployments:

- **Reproducibility as a template.** Other RCMs and partner organisations need to be able to build their own instance from a shared template. Some third-party platforms support this directly. SharePoint Lists doesn't: gaining the correct permissions to create or replicate a list structure has taken months of back-and-forth, with inconsistent setups, across three institutions RCM Cooperative has worked with.
- **Avoiding platform lock-in.** Some options, notably SharePoint, require an organisation to already hold, or purchase, a wider commercial ecosystem licence (Microsoft 365) beyond the tool itself. A dedicated, independent cloud tool avoids this dependency.
- **Barrier to entry for deployment.** A fully self-hosted design requires either a central IT team to provision server infrastructure, or each adopting organisation to independently set up and maintain Docker-based hosting. This barrier exists by design, and self-hosting can't avoid it.

This assessment is organised around **barrier to entry**, not a simple binary choice between self-hosting and third-party platforms.
Self-hosting scores highest on data privacy and control, and remains the right choice for deployments where the infrastructure burden is acceptable — for example, where a dedicated IT team is already available, and templated reuse matters less.
For other deployments, particularly where the goal is a low-barrier template other RCMs can adopt themselves, a well-vetted third-party platform is more accessible, provided you've properly assessed and documented its data-handling safeguards rather than assumed them.

This is a genuine trade-off: choosing a third-party platform buys accessibility and templatability, at the cost of depending on an external party's data-handling safeguards rather than controlling the infrastructure directly.
It isn't a limitation-free choice.
The open items in Table 2 and Table 3 are the gap you need to close before you can consider this trade-off fully assessed for a given deployment.

See also `baserow/self-hosted-vs-cloud.md` for a dedicated comparison of self-hosting Baserow itself against using Baserow Cloud, once the four-way comparison below has narrowed the choice to Baserow.

## Options assessed

This assessment compares four options, ordered from most technically complex and highest-control to lowest-barrier:

1. **Self-hosted SQL (SQLite/Postgres)** — the original RCM-CRM architecture. See `self-hosted-architecture/architecture-self-hosted-technical.md` for the full technical design; this document references it for comparison rather than repeating it.
2. **SharePoint Lists** — a Microsoft 365-based list/table structure.
3. **SeaTable** — a cloud-hosted, open-core table/database platform.
4. **Baserow** — a cloud-hosted, or self-hostable, fully open-source table/database platform.

## Table 1: Design requirements comparison

### Hosting & openness

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Hosting requirement | Requires provisioning and maintaining your own server, or a Postgres instance | Cloud-hosted, if your institution already holds M365 | Cloud-hosted; no server required | Cloud-hosted, or self-hostable; no server required unless you choose self-hosting |
| Open source | ✅✅ Fully open source, self-built | ❌ Fully proprietary | ⚠️ Open-core; the Cloud tier is proprietary | ✅✅ Fully open source (MIT), self-hostable |

### Adoption & lock-in

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Reproducible as a template other organisations can self-deploy | ⚠️ A template (Docker Compose plus schema) exists and is designed for cloning, but each adopter still needs to provision and run their own infrastructure | ❌ The institutional permissions process has taken months, with inconsistent setups, across three institutions | ⚠️ Not yet tested at this depth | ⚠️ Not yet tested at this depth |
| Avoids platform or ecosystem lock-in | ✅✅ No dependency on any external platform | ❌ Requires the receiving organisation to already hold, or purchase, M365 licensing | ✅ | ✅ |

**A note on "avoids lock-in," precisely stated.** The claim above is narrower than it might first read: it means these platforms don't force you to also buy into a *second*, larger commercial ecosystem (unlike SharePoint's M365 dependency), not that you're free of any dependency at all. Two further, more specific points worth separating out:

- **Vendor-existential lock-in.** Baserow is fully open source (MIT), and the same software can be self-hosted, not just used as their Cloud product — so the "escape hatch" isn't just "export your data," it's "keep running the identical software yourself if the vendor disappears or changes terms unfavourably." SeaTable's position here is weaker: this escape hatch only exists for its Community (self-hosted) edition, not the proprietary Cloud tier this project has actually used — the two shouldn't be scored identically on this point.
- **Structured JSON export, not just flat CSV.** Both Baserow's workspace-export mechanism and its field-definitions API return the actual *schema* (field types, formulas, link relationships, select options) via a documented, open format — not just row values. This is a genuine interoperability property distinct from open-source licensing: it means migration or independent tooling doesn't depend on the vendor's own export UI. See `baserow/schema.md` for how this has been used in practice on this project.

What genuinely isn't avoided: dependency on Baserow-the-company for the Cloud product actually in use day to day (pricing, feature, or continuity risk), and schema/paradigm lock-in — your data model is built around Baserow's specific concepts (tables, link fields, formulas), and moving to a fundamentally different kind of tool still means remapping that structure, even with full export in hand.

### Working with data

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Import from CSV/XLSX, with a preview and validation before committing | ✅✅ Fully controllable — validation is whatever you choose to build, from none to arbitrarily strict | ❌ Import-from-Excel only creates a **brand-new list**; you can't import additional rows into an existing list this way. Adding data later needs manual grid copy-paste (no validation beyond column type) or a custom Power Automate flow. Some column types, such as Hyperlink, People, and Location, aren't available through this route at all | ✅ Genuine preview before committing, with a choice of which columns to import; Excel imports attempt automatic column-type detection. The preview caps at 201 rows even for larger files, and CSV imports don't get the same type detection Excel imports do. **Not confirmed, but assumed to share Baserow's limitation below**: likely imports plain values only, not linked-record relationships | ✅✅ Genuine preview before committing, both for new tables and for importing into an **existing** table — toggle between "Import Preview" (how it'll land) and "File Content" (the raw source) to compare. Column headers auto-map to matching field names, with manual remapping if they don't match. Respects existing field types (dates stay dates, single-select values are matched or created) rather than flattening everything to text. Supports an **upsert** mode — update matching rows by a unique identifier instead of only appending — which neither SeaTable nor SharePoint offer natively. New-table imports are capped at 5,000 rows. **Confirmed limitation**: import populates plain field values only — it does not resolve or create Link-to-table relationships. Linked-record fields need to be set up separately after import, not through the CSV/XLSX import step itself |
| Duplicate detection/prevention | ⚠️ Fully controllable, but must be built — this project's own design already anticipates the need (see the fuzzy-matching limitation noted for SeaTable below, which a self-hosted build could in principle solve properly, at real development cost) | ⚠️ Native **"Enforce unique values"** per column, exact match, blocks at entry. Limited to a single column only — no native way to enforce uniqueness across a combination of columns (e.g. name + organisation together); that needs a Power Automate flow. Does not catch duplicates already present, or introduced via bulk import/scripts | ⚠️ Two native, complementary tools: **"Prevent duplicates when adding records"** on a Form (blocks at entry) and **"Highlight duplicates"** conditional formatting on the grid (flags existing duplicates, doesn't block). Both exact-match only (case-insensitive with a normalisation column); no fuzzy or word-order-invariant matching (for example, "University of Manchester" vs "Manchester University" won't be caught) | ⚠️ Native **unique field-value constraint**, blocks duplicate entries at creation or update time. Also a **"Unique" footer aggregation** to spot non-unique values in a column at a glance. Same limitation as the others: strict string comparison only — trailing spaces or reordered words are treated as different values, so no fuzzy matching. See `baserow/training.md` for how RCM Cooperative's own duplicate-detection automation was built, using a self-referencing link and a Count field, on top of this native constraint |
| Data export and portability, for example to CSV or XLSX | ✅✅ Not applicable — this is your own database; export it however you choose, including a full SQL dump | ✅ Straightforward | ✅ Straightforward, but formulas and link relationships don't survive export | ✅ Straightforward |
| Kumu.io export preparation, from the same executable | ✅ | ✅ | ✅ | ✅ |

The residual lock-in risk for the third-party platforms is about ecosystem dependency, such as SharePoint's M365 requirement, not data portability — export is straightforward across all three.

### Presenting & sharing data

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Ease of building a dashboard summarising the data | ❌ No native dashboard; requires custom-built reporting — see the Jupyter notebook reporting design in `self-hosted-architecture/architecture-self-hosted-technical.md` | ⚠️ Native "Visualize the list" was retired in November/December 2025; dashboards now need licensed Power BI, or the limited Quick Chart web part | ✅ Native, using the Statistics module | ✅ Native, using bar and line widgets (in beta — verify before relying on this) |
| Two-tier access: a small group with edit access, and a public, limited view | ✅ Fully controllable, but you must build it; consent tiers are already designed into the schema | ❌ Anonymous links work only per item, not per list; SharePoint provides no way to hide fields from anonymous viewers | ✅ Read-only sharing with roles | ✅ Read-only public links, with password protection |
| Drill-down/data-leak risk on the public view | ✅ No risk — the public output is a separate, deliberately pseudonymised export, not a live view into the database | ⚠️ Confirmed risk: Power BI row-level security doesn't apply to anonymous access | ⚠️ Unresolved | ✅ Resolved — fields stay hidden |
| Reproducible reporting (PDF or template) | ✅ Using version-controlled Jupyter notebooks and Pandoc — already designed | ✅ Power BI reports are reproducible, but require Pro or Premium licensing per viewer | ✅ Native, using Page Design (stable) or Report Design (beta) | ❌ No native PDF output; only third-party workarounds |
| Unified UI, embedding a dashboard and a Kumu map together | ⚠️ Fully controllable, since it's custom-built, but nothing exists out of the box — you must develop it | ❌ One-way only: you can embed content into SharePoint, but Microsoft blocks embedding SharePoint content elsewhere | ⚠️ Unconfirmed in either direction | ✅✅ Confirmed in both directions, using the native IFrame element and embeddable public views |

### Data model & relationships

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Relationships between tables are bi-directional by default | ✅✅ Fully controllable by design — a relational join is inherently two-way | ❌ One-directional only: adding a lookup on List A doesn't create or update anything on List B. A true reverse link needs a second, separately maintained lookup column, a display-only "Related List" web part, or a paid third-party add-on | ✅ Native — linking a record on one table automatically creates and updates the reverse field on the other | ✅ Native — linking a record on one table automatically creates and updates the reverse field on the other |
| Limits on the number of relationship (lookup) columns | ✅✅ None | ⚠️ A view can show a maximum of **12 lookup-type columns**, and this cap includes built-in system columns such as Created By and Modified By, which already use two of the twelve before you add any of your own | ⚠️ Not confirmed — worth checking before relying on a high number of link columns per table | ⚠️ Not confirmed — worth checking before relying on a high number of link columns per table |
| Manual upload/parse via local executable | ✅ Direct database access; no API layer needed | ⚠️ REST/Graph API exists but needs Azure AD app registration (OAuth) — more setup | ✅ REST API and Python client | ✅ REST API |
| A computed/formula field can be set as the primary field | ✅✅ Fully controllable — any derived identifier can be defined | ❌ The Title/primary field cannot be a genuinely calculated field in the way needed here, for example a live first + last name concatenation — a long-standing SharePoint limitation | ✅ Supported since SeaTable 3.5 (2023); earlier versions restricted the first column to Text, Number, Date, Single Select, or Auto Number only | ✅ Natively supported and explicitly recommended by Baserow's own documentation for exactly this case — combine multiple fields into a Formula field and set it as the primary field |

This is closely related to duplicate detection, in the "Working with data" cluster above: a computed primary field derives a reliable, canonical identifier from raw fields (for example, name plus email) rather than relying on someone typing a consistent value by hand, and that same derived, normalised value is what makes duplicate detection possible in the first place.

**Net assessment:** Baserow leads on open source, and resolves two items SeaTable leaves open: the drill-down risk, and unified UI embedding. SeaTable's advantage is native PDF reporting. SharePoint is the weakest technical fit — one-directional lookups and a 12-lookup-per-view cap add real friction to any multi-table relationship model like this one — and its one structural advantage, discussed in Table 3, is undercut by real, repeated deployment friction.

## Table 2: Privacy and data residency comparison

### Data controller: where the data lives, and who controls it

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Data hosting location and jurisdiction | ✅✅ Wherever the deploying organisation chooses, fully within its own control | ⚠️ Depends on the host institution's tenant provisioning | ✅ Germany (EU/GDPR) | ✅ Germany (EU/GDPR); Dutch company |
| Company or ownership structure, and non-EU access | ✅✅ Not applicable — no external company holds the data | ⚠️ US company (Microsoft), subject to the US CLOUD Act — not confirmed in writing | ⚠️ Chinese sister company (Seafile) under a joint venture — not confirmed in writing | ⚠️ Dutch company — not confirmed in writing |
| Data residency: stays within the host institution's own infrastructure | ✅✅ Stays entirely within the deploying organisation's own infrastructure — no vendor relationship of any kind | ✅ Stays within the institution's existing Microsoft tenant and governance boundary, though it's still physically Microsoft's cloud | ❌ Third-party vendor relationship | ❌ Third-party vendor relationship |

### Contractual safeguards

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Data Processing Agreement | ✅✅ Not applicable — no data processor relationship exists | ✅ Exists (the M365 DPA); not yet read against this project | ✅ Exists; not yet read in full | ✅ Exists; not yet read in full |
| Technical and Organisational Measures | ⚠️ Must be self-defined and documented by whoever hosts the deployment, rather than inherited from a vendor | ⚠️ Not found as a standalone document; bundled into the Trust Center and ISO documentation | ⚠️ Not found as a standalone document | ⚠️ Not found as a standalone document |
| International transfer safeguards, such as Standard Contractual Clauses | ✅✅ Not applicable, unless the deploying organisation chooses to host outside its own jurisdiction | ✅ The DPA explicitly includes EU SCCs and a UK Addendum | ⚠️ Question drafted, not yet sent. Ask SeaTable directly: "Do you rely on Standard Contractual Clauses, or an equivalent safeguard, to cover any transfer of our data outside the EU/UK, including any access by Seafile Ltd. or other non-EU entities under your joint-venture structure? Please provide the relevant SCC documentation or equivalent." | ⚠️ Same open question. Ask Baserow directly: "Do you rely on Standard Contractual Clauses, or an equivalent safeguard, to cover any transfer of our data outside the EU/UK, including any subprocessors involved in delivering the service? Please provide the relevant SCC documentation or equivalent." |

### AI-related risk

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| AI or model-training use of customer data | ✅✅ Not applicable in the core design; any local-LLM use stays on-device, per the main CRM's local AI design | ⚠️ Not used for training by default, but this depends on whether Copilot is enabled — Flex Routing can send data outside the EU boundary | ✅ The Cloud tier can't connect an external LLM provider; SeaTable states it doesn't use customer data for training | ✅ EU-hosted, tenant-isolated; no database access for AI features |

**Open items to resolve for whichever platform you choose:** read the full TOM document for that platform, get written vendor confirmation on non-EU or non-UK data access under the DPA/SCC terms, and, for Baserow specifically, confirm whether Dashboards, not just Grid, Gallery, or other views, can be shared publicly.

## Table 3: Barrier to entry and justification

This table sets the third-party options against the self-hosted design, using barrier to entry as the organising concept rather than privacy alone — privacy and control are covered in full in Table 2.

### Infrastructure requirements

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Physical infrastructure | ❌ Requires a server, or a Postgres instance, to be provisioned and maintained | ✅ None beyond an existing M365 tenant, if already held | ✅ None — cloud-hosted | ✅ None — cloud-hosted, or self-hostable later if desired |
| People infrastructure | ❌❌ Requires an IT team, either RCM Cooperative's or the adopting organisation's, to provision and maintain infrastructure | ❌ Requires institutional IT/governance involvement to grant list-creation permissions — a lengthy, inconsistent process across three institutions | ✅ None beyond the individual signing up for a cloud account | ✅ None beyond the individual signing up for a cloud account |
| Technical infrastructure | ❌ Requires Docker and database setup/configuration knowledge | ❌ Requires an existing M365 licence as a precondition | ✅ Sign up and use directly | ✅ Sign up and use directly |

### Platform or ecosystem lock-in

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Platform or ecosystem lock-in | ✅ None | ❌ Requires buying into the M365 ecosystem | ✅ None | ✅ None — open source, and self-hostable later if needed |

### Deployable as an openly licensable self-serve template

Whether a template can genuinely be released as open (for example, under CC-BY) depends on whether the underlying platform imposes an unavoidable licensing cost on recipients, not just on the licence you put on your own content.
Your own schema design — table structures, field names — is your own content, created using the platform as a tool; a platform's terms don't restrict what licence you apply to content you created yourself.
What matters is whether a recipient has a genuinely free path to actually *use* what you release.

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Deployable as an openly licensable self-serve template | ✅✅ Fully open — MIT-licensed software, zero licensing cost floor for any recipient | ❌ No free path exists at all — even a CC-BY-licensed template still requires the recipient to hold, or purchase, M365 | ⚠️ Open-core: a genuinely free path exists only if the recipient self-hosts the open-source edition, not via the proprietary Cloud tier | ✅ MIT-licensed and self-hostable — a genuinely free path exists. Sharing a template between separate Cloud accounts isn't a polished "install from a link" experience yet (no public marketplace for user-submitted Cloud templates), but workspace export/import — structure-only, explicitly described by Baserow as "ideal for creating templates for others to fill in" — works cleanly and matches RCM-CRM's existing clone-the-template pattern |

**Confirmed process (tested directly, September 2026):** Home → click the workspace name text + its chevron at the top of the page (not the sidebar account-switcher icon, and not a per-database three-dot menu — both look plausible but don't have this option) → **Export data** → select which databases to include → tick **"Export structure only"** to exclude row data → Export. Recipients import via the mirror path: Home → their workspace name + chevron → **Import data** → upload the ZIP. Full click-path and further findings are in `baserow/training.md`.

Two things worth knowing before relying on this:
- **Automations are not selected by default** in the export dialog — must be manually ticked, or automations such as the duplicate-detection workflow won't transfer to an imported copy.
- **Confirmed directly with Baserow support:** workspace export/import works on the **Free plan**, contradicting an earlier assumption (drawn from Baserow's own pricing-page wording, which only mentions CSV export for Free) that this required a paid tier. Paid-tier features used during a trial (e.g. a Timeline view) still get included in an export, but deactivate if imported into a Free-tier instance — the import itself isn't blocked, just those specific features go inactive. Since this project's template doesn't use any premium-only view types, this has no practical effect here.

### The trade-off, stated plainly

Choosing Baserow, or a similar third-party platform, over the self-hosted design means a third-party data processor handles personal data about community members, rather than that data remaining entirely within RCM Cooperative's, or a client's, own infrastructure.
This is a deliberate choice made for accessibility and templatability. It isn't a limitation-free upgrade.

Don't adopt a third-party platform for a given deployment until you've resolved the open items in Table 2.
Document and justify each deployment's platform choice individually against this table, rather than defaulting to a previous choice without reassessment.

## Table 4: Self-service update form

A further requirement, not covered above: letting an individual community member view and update their own record directly, without staff involvement, and without granting them broader database access.

This is genuinely complicated to get right — it touches identity verification, access control, infrastructure availability, and a review workflow, all at once.
It's worth the complexity because of what it gives the community in return: rather than depending entirely on an RCM to maintain their record correctly, individuals get direct agency over their own data — the same principle behind treating community visibility as a shared asset, not just a management tool (see `why-crm.md`).

### Infrastructure required for user self-serve

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Infrastructure required for user self-serve | ⚠️ Requires the correction form to be built (planned, not yet built), and requires the hosting machine to be always-on and internet-reachable when someone submits — a real constraint given this architecture's deliberately intermittent-uptime design. Also needs HTTPS, for example through a tunnelling service, for the form link to work externally | ❌ No native path exists at all; custom development is needed regardless of infrastructure | ⚠️ Cloud-hosted, so always available — this removes the uptime concern entirely, but it's moot given SeaTable doesn't natively support editing an existing record at all (see below) | ✅ Cloud-hosted, always available — lowest infrastructure burden of the four |

### Access requirements for user self-serve

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Access requirements for user self-serve | ✅ Fully controllable — the already-designed v2 form can use ORCID authentication or a token-based link, with no separate account needed either way, since it's your own build | ❌ No native equivalent; a custom Power Automate flow would need its own access mechanism, likely an M365 guest/external account | ⚠️ Not meaningfully assessable, since editing an existing record isn't natively supported (see "Serving new and existing users" below) | ✅ No account or workspace access needed at all — a unique, cryptographically secure per-row link is the only credential |

### Serving new and existing users with a pre-populated form

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Serving new and existing users with a pre-populated form | ✅ Fully controllable — pre-fill and a pending-review step are already part of the v2 design | ❌ No native way to edit an existing item through a public-facing form; requires custom development, not just configuration | ❌ Web forms appear to create new rows only, not edit existing ones — not confirmed to support updating an existing record at all | ⚠️ Native, using the **Edit row link** field: pre-fills the form with that row's current data and updates that specific row on submit. Writes directly to the live row, with no native pending-review step |

### Native alerts to admins on new or changed entries

| Requirement | Self-hosted SQL | SharePoint Lists | SeaTable | Baserow |
|---|---|---|---|---|
| Native alerts to admins on new or changed entries | ⚠️ Fully controllable, but must be built — no platform to inherit this from | ⚠️ Native "Alert Me" exists today, but SharePoint Online is fully retiring it in **July 2026**; Microsoft's recommended replacement is native "Rules" (still built-in, no extra cost) or Power Automate for more complex logic | ✅ Native **Notification Rules**, available on the free tier — trigger on entries added or changed, with optional filter conditions, delivered in-app and by email to selected users | ⚠️ Native form-submission notifications (in-app and email, free, one toggle) cover "someone submitted an edit" directly. Broader row-created/updated alerts need a **webhook** connected to an external tool or a small script — not fully native |

### Reconciling the pending-review gap

Baserow's Edit row link is the strongest option on ease of submission and access requirements, but writes directly to the live row, with no native review step — a gap against the pending-review requirement established for this project.

The recommended approach: point the Edit row link form at a **separate staging table**, rather than the live table directly, and write a small comparison script (for example, using the Baserow API) that diffs staging rows against the corresponding live rows and surfaces the changed fields for staff review. This mirrors the pending-review table pattern already designed into the self-hosted v2 architecture, implemented inside Baserow rather than built from scratch. Adding a **"Last Modified By"** field to the staging table is worth doing at the same time — Baserow's webhook payload then automatically includes who made the change, useful context for the reviewer at no extra build cost.

## Outcome

For deployments that prioritise ease of adoption and reproducibility as a template, for example RCM Cooperative's own CRM and future self-serve deployments by other RCMs, **Baserow** is the current recommended platform, once you've resolved the open privacy-verification items above and before you enter any live personal data.

For deployments with dedicated institutional IT infrastructure already in place, where a third-party processor relationship isn't desired or appropriate, the **self-hosted SQL design** remains the recommended architecture.
