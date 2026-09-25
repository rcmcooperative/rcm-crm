# RCM CRM

[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)

## About this Repository

This repository contains the documentation, research materials, and outputs for the **RCM-CRM project**, developed by the [RCM Cooperative](http://rcmcooperative.com/).

This project follows open research principles to deliver FAIR and openly licensed materials. Publication of these materials supports transparency in this project, and reproducibility of similar work. All materials from the project are published as open as possible, as closed as necessary.

This repository builds on the template created and maintained by *The Turing Way* team members and shared under CC-BY 4.0 for reuse: [https://github.com/alan-turing-institute/reproducible-project-template](https://github.com/alan-turing-institute/reproducible-project-template).

Note after pulling a local copy of this repo, you may wish to create an additional directory called `private`. Use this directory to enable files to be stored locally without being included in the main repo (this directory is excluded by the [.gitignore](~/.gitignore)). This is useful where there are restrictions on sharing some information (GDPR) or license terms are yet to be agreed. See [Repository structure](#repository-structure) below for what lives where.

## AI Use

Some materials in this repository — including the drafting and editing of the step-by-step training documentation in `docs/baserow/training/` — were prepared with the assistance of Claude (Anthropic), used interactively by a human author who directed, reviewed, and edited the output rather than publishing it unread.

This is separate from the AI use inside the CRM's own skills (see [Repository structure](#repository-structure) below): those are marked explicitly as **\[uses an LLM\]** or **\[deterministic code, no LLM\]** per skill, reflecting whether live CRM data is ever exposed to a model — a distinct question from whether AI assistance was used to help write documentation *about* the CRM.

Confirm the exact wording and scope of this disclaimer against RCM Cooperative's own AI-use policy, if and when one exists, before treating this as final.

## Vision and Mission

- **Vision:** Research community managers everywhere have open, privacy-conscious, ethical tools for understanding and growing their communities.
- **Mission:** To build and maintain an open-source CRM for Research Community Managers (RCMs), enabling transparent, GDPR-aware community engagement tracking — designed to be cloned and adapted by any research community.

## About

The RCM-CRM is an open-source Customer Relationship Management (CRM) system for Research Community Managers (RCMs), built by the RCM Cooperative.

**Current architecture is Baserow-based** — see `docs/baserow/architecture-overview.md` and `docs/baserow/schema.md` for the full design. An earlier self-hosted SQL/SQLite design remains documented as an alternative, still the right choice for deployments needing full infrastructure control (see `docs/self-hosted-architecture/`), but is not what RCM Cooperative's own CRM currently runs on. Full rationale for the platform choice: `docs/platform-needs-assessment.md`.

It replaces a prior SharePoint-based MVP — the [RCM Cooperative Community Mapping Workflow](https://github.com/rcmcooperative/community-mapping) — retaining [Kumu](https://kumu.io/) as the public-facing visualisation layer.

Designed from the outset to be cloned and handed off to individual client communities, via Baserow's own workspace export/import mechanism (structure-only export, no client data) — see [Chapter 2: Entering data](docs/baserow/training/02-entering-data.md) in the training documentation for the confirmed process.

**New to running this CRM day-to-day?** Start with the step-by-step training documentation in [`docs/baserow/training/`](docs/baserow/training/) — six chapters covering designing the visualisation, entering data, maintaining your data, enabling self-serve editing, downloading your data, and managing the Kumu visualisation.

## Roadmap & Milestones

Status cross-checked against the current system overview diagram (`assets/images/overview_drawio.png`).

### v1 — Baserow build

**Database and data model**

- [x] Baserow workspace: five tables (People, Organisations, Communities, Interactions, Projects), full relationship mesh — see `docs/baserow/schema.md`
- [x] Computed/formula primary fields (long name + abbreviation)
- [ ] Duplicate-contact detection — tested for People (custom Baserow self-link-on-name-match automation) but not stable. For a more robust approach, see Baserow's own guidance on [advanced deduplication via webhooks and external automation](https://baserow.io/user-docs/edit-rows-via-form) — worth evaluating as an alternative to the current automation.

**Data ingest**

- [x] Meeting notes → Interactions (`crm-notes-extraction` skill, uses an LLM)
- [x] Google Contacts/email matching → People (`crm-email-contacts` skill, deterministic code, no LLM)
- [x] Community sign-up form
- [x] Slack member export parsing (`crm-slack-extraction` skill, deterministic code, no LLM) — public channels only, per the current Free-tier workspace plan
- [ ] Zoom/call attendee export parsing
- [ ] GitHub contributions parsing
- [ ] Zenodo contributions parsing

**Kumu export** (`crm-kumu-visualisation` skill, deterministic code, no LLM)

- [x] Baserow → Kumu pipeline built: produces separate internal (full data) and public (consent-filtered) workbooks, generic edge types, stable pseudonymisation hash — see `docs/baserow/schema.md` for the full edge/consent registry
- [ ] Two design assumptions flagged for review: the `affiliated` edge type for `Communities.organisations`/`Projects.communities`, and whether excluding (not just pseudonymising) people without public consent from the public export is the intended policy

**Web App** (data ingest UI, dashboard, mailing list integration — distinct from the Kumu export pipeline above, which is already built)

- [ ] Not yet built — see `docs/baserow/architecture-overview.md`

**Self-serve** (consent, re-confirmation, correction, addition via pre-populated row link)

- [x] Baserow's native Edit row link field generates unique per-row URLs that can be sent privately, pre-filled with the row's current data
- [ ] The originally-planned staging-table/review step before changes hit the live table is not implemented — a submission via this link currently writes directly to the live row

**Publishing and templating**

- [x] Public database template — workspace export/import confirmed working, including on Baserow's Free tier
- [x] Public data map (Kumu) — via the `crm-kumu-visualisation` pipeline above, individuals appear at their given consent level (excluded, pseudonymised, or identifiable)

**Documentation**

- [x] Step-by-step training documentation (`docs/baserow/training/`, six chapters) — Chapters 1–5 complete; Chapter 6 (Managing the visualisation) in progress
- [ ] Reproducible deployment write-up, CC-BY 4.0/MIT materials on GitHub (this repository)

**Mailing list**

- [ ] Platform not yet chosen — TBC, see `docs/baserow/architecture-overview.md`

### v1.1+ / v2

- [ ] Resolve whether ORCID OAuth is still needed for self-service, now that Baserow's native Edit row link provides a working (if unreviewed) self-serve mechanism
- [ ] Add a pending-review/staging-table step in front of the Edit row link, to close the gap flagged above
- [ ] Email marketing/comms tooling integration (e.g. Mailchimp, Yet Another Mail Merge)
- [ ] NLP/chatbot-based contact entry
- [ ] Photo/name-tag OCR entry (vision-capable local model)
- [ ] Federated cross-community data exchange
- [ ] Self-hosted Baserow deployment option, for clients where the third-party-processor relationship in `docs/platform-needs-assessment.md` (Table 2) is a blocker — see `docs/baserow/self-hosted-vs-cloud.md`
- [ ] Reusable/API-driven duplicate-detection automation, rather than manually rebuilt per table — see Baserow's advanced-deduplication guidance linked above
- [ ] MOE (Mountain of Engagement) stage tracking and visualisation in Baserow itself — the conceptual framework is documented (`docs/engagement-framework.md`, currently marked for review) but not yet implemented as live Baserow fields/views
- [ ] Stalled/at-risk flagging (no recent interaction) — conceptually descriptive-only by design (see `docs/why-crm.md`), not yet implemented in Baserow
- [ ] Tagging/segmentation, with optional local-model-suggested tags based on interaction content
- [ ] Communication log (outreach sent, separate from interactions received)
- [ ] Reporting via version-controlled Jupyter notebooks, pseudonymised IDs only, read-only DB connection
- [ ] Resolve the two flagged Kumu pipeline assumptions above, and revisit generic vs. per-table-pair edge typing once the graph itself clarifies the Organisation/Community and Project/other-table boundaries
- [ ] Internal-only `mission-interest`/`mission-influence` fields on the `People` table, for the internal Kumu map only — see [Chapter 6: Managing the visualisation](docs/baserow/training/06-managing-the-visualisation.md)

## The Team

| Name | Affiliation | ORCID | GitHub |
| --- | --- | --- | --- |
| Cassandra Gould van Praag | RCM Cooperative | [0000-0002-8584-4637](https://orcid.org/0000-0002-8584-4637) | [@cassgvp](https://github.com/cassgvp) |
| Emma Karoune | RCM Cooperative | [0000-0002-6576-6053](https://orcid.org/0000-0002-6576-6053) | [@EKaroune](https://github.com/EKaroune) |
| Malvika Sharan | St Jude Children's Research Hospital | [0000-0001-6619-7369](https://orcid.org/0000-0001-6619-7369) | [@malvikasharan](https://github.com/malvikasharan) |

## Repository structure

```
rcm-crm/
├── README.md                          # this file
├── CLAUDE.md                          # project context for Claude Code sessions
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE.md
├── .all-contributorsrc
│
├── .github/
│   └── ISSUE_TEMPLATE/                 # community-call, contributor-bio, event, funding-application, new-members, sunsetting
│
├── docs/
│   ├── README.md                      # documentation index
│   ├── why-crm.md                     # the case for this tool; architecture-agnostic
│   ├── engagement-framework.md        # MOE, influence/interest — currently marked NEEDS REVIEWING
│   ├── data-privacy-assessment.md     # generic DPIA template, complete per deployment
│   ├── platform-needs-assessment.md   # Baserow vs. SharePoint vs. SeaTable vs. self-hosted SQL
│   │
│   ├── baserow/                       # current, live architecture
│   │   ├── architecture-overview.md
│   │   ├── schema.md
│   │   ├── self-hosted-vs-cloud.md
│   │   └── training/                  # step-by-step training documentation, six chapters
│   │       ├── 01-designing-the-visualisation.md
│   │       ├── 02-entering-data.md
│   │       ├── 03-maintaining-your-data.md
│   │       ├── 04-enabling-self-serve-editing.md
│   │       ├── 05-downloading-your-data.md
│   │       └── 06-managing-the-visualisation.md
│   │
│   └── self-hosted-architecture/      # alternative deployment option, not the current build
│       ├── README.md
│       ├── architecture-self-hosted-technical.md
│       └── architecture-self-hosted-lay-summary.md
│
├── assets/
│   ├── baserow-structure/             # exported workspace template (structure-only ZIP)
│   │   └── structure-exports/         # dated snapshots of the live schema, pulled via the API
│   │       └── YYYY-MM-DD/
│   └── images/                        # diagram PNGs, training screenshots, and editable source (source/)
│
├── project-management/
│   ├── team.csv                       # subset of the full team roster, selected per project
│   ├── communications/
│   ├── meeting-notes/
│   └── reports/
│
└── .claude/
    └── skills/
        ├── crm-notes-extraction/      # meeting notes → Interactions [uses an LLM — claude-cloud]
        ├── crm-email-contacts/        # Google Contacts matching → People [deterministic code, no LLM]
        ├── crm-slack-extraction/      # Slack export → People/Interactions [deterministic code, no LLM]
        ├── crm-kumu-visualisation/    # Baserow exports → Kumu elements/connections [deterministic code, no LLM]
        └── populate-repo-template/    # fills this template's README/CONTRIBUTING/CoC placeholders [uses an LLM]
```

Skills marked **\[deterministic code, no LLM\]** never send CRM data to a model — the privacy concern they're designed around is exposure of personal data to a model's reasoning, not code reading it. Skills marked **\[uses an LLM\]** do, and are chosen where the task (unstructured text extraction, filling template prose) genuinely needs interpretation rather than a fixed transform.

This tree omits `private/` (gitignored working data — meeting notes, Slack exports, email-contact matching, Kumu intermediate files — not part of the repository itself), `.git/`, `.DS_Store` files, and other dotfiles not listed above.

Two stray repository-tree dump files currently sit at the repo root (`directory_tree.txt` and `directory-tree.txt`) — now that this section is the maintained, up-to-date tree, these should be deleted rather than kept in sync separately. `skill-reference-user-nominated-fields-treatment.txt` at the repo root also looks like a working/scratch file rather than a finished doc — confirm whether it should be deleted or moved into `docs/` before the next push.

## Contributing

- **Guidelines:** [Contribution Guidelines](CONTRIBUTING.md) for contributors.
- **Code of Conduct:** [Code of Conduct](CODE_OF_CONDUCT.md) ensures a respectful project environment.

## Licensing

This project is licensed under the CC-BY-4.0 License for documentation and MIT license for code - see the LICENSE.md file for details.

## Citing & Acknowledgement

This project builds on the [RCM Cooperative Community Mapping Workflow](https://github.com/rcmcooperative/community-mapping):

> Gould van Praag, C. (2025). RCM Cooperative Community Mapping Workflow (v1.0.0). Zenodo. [https://doi.org/10.5281/zenodo.15320348](https://doi.org/10.5281/zenodo.15320348)

To cite this repository, please use the information in [`CITATION.cff`](CITATION.cff) once it has been added — see the setup checklist below.

## Contact

Reach out to [Cassandra Gould van Praag](https://github.com/cassgvp) at [cassandra.gouldvanpraag@rcmcooperative.com](mailto:cassandra.gouldvanpraag@rcmcooperative.com) with questions, feedback, or ideas.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

| [![Cassandra Gould van Praag](https://avatars.githubusercontent.com/u/43407869?v=4?s=100) **Cassandra Gould van Praag**](https://github.com/cassgvp) [💻](https://github.com/rcmcooperative/rcm-crm/commits?author=cassgvp) [📖](https://github.com/rcmcooperative/rcm-crm/commits?author=cassgvp) [🤔](#ideas-cassgvp) | [![Emma Karoune](https://avatars.githubusercontent.com/u/58147174?v=4?s=100) **Emma Karoune**](https://www.turing.ac.uk/people/research-associates/emma-karoune) [🤔](#ideas-EKaroune) | [![Malvika Sharan](https://avatars.githubusercontent.com/u/5370471?v=4?s=100) **Malvika Sharan**](http://malvikasharan.github.io/) [🤔](#ideas-malvikasharan) |
| --- | --- | --- |

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

Note we are currently using locally installed all-contributors while this repo is private. Add contributors locally using the below command in a terminal then push changes.

`npx all-contributors-cli add malvikasharan ideas`

## Checklist for setting an online repository

This repo has been templated from the [RCM Cooperative Partner template repo](https://github.com/rcmcooperative/partner-template), including file structure, starter contents and a Claude Skill to fill in template information.

After running the Claude skill, please review the list below to and check off once completed.

This repo includes:

- [ ] A meaningful and accurate README.md
- [ ] A meaningful and accurate [CONTRIBUTING](CONTRIBUTING.md) file
- [ ] A [LICENSE](LICENSE.md) (we suggest MIT for code and CC-BY-4.0 for documentation)
- [ ] A [Code of Conduct](CODE_OF_CONDUCT.md) (we suggest RCM Cooperative CoC)
- [ ] A directory for project management (communications, meetings, reports, proposals)
- [ ] A directory for assets (non-code supporting files such as images, diagrams, templates, and similar media) that are used in the projects documentation or output)
- [ ] A directory for documentation
- [ ] Directories for any research materials if appropriate for the project (ethics, data, analysis)
- [ ] Ready to use [all-contributors](https://allcontributors.org/) bot (installed for the RCM Cooperative GitHub organisation)
- [ ] Appropriate issue templates
- [ ] Appropriate .gitignore file
- [ ] Connect repo with Zenodo the order of these needs to be reviewed
- [ ] Add cff file for citation (we suggest creating this with [https://bit.ly/cffinit](https://bit.ly/cffinit))
- [ ] Add a DOI badge (see the zenodo doi badge widget)