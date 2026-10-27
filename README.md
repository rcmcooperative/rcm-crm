# RCM CRM

[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)

[![DOI](https://zenodo.org/badge/1285339502.svg)](https://doi.org/10.5281/zenodo.23692251)

## About this Repository

This repository contains the documentation, research materials, and outputs for the **RCM-CRM**, developed by the [RCM Cooperative](http://rcmcooperative.com/).

We are pleased to share this project with you openly as part of our ongoing development. If you stop any errors or gaps (which there surely will be!), we'd love for you to share them with us! See our [CONTRIBUTING](./CONTRIBUTING.md) guide.

All contributors to this project are requested to follow RCM Cooperatives [Code of Conduct](CODE_OF_CONDUCT.md).

This project follows open research principles to deliver FAIR and openly licensed materials. Publication of these materials supports transparency in this project, and reproducibility of similar work. All materials from the project are published as open as possible, as closed as necessary. Documentation is shared under CC-BY 4.0 and code under MIT. See our [LICENSE](LICENSE.md) for more details.

Note after pulling a local copy of this repo, you may wish to create an additional directory called `private`. Use this directory to enable files to be stored locally without being included in the main repo (this directory is excluded by the [.gitignore](~/.gitignore)). This is useful where there are restrictions on sharing some information (GDPR) or license terms are yet to be agreed. See [Repository structure](#repository-structure) below for what lives where.

## Vision and Mission

- **Vision:** Research community managers everywhere have open, privacy-conscious, ethical tools for understanding and growing their communities.
- **Mission:** To build and maintain an open-source Community Relationship Management (CRM) system for Research Community Managers (RCMs), enabling transparent, GDPR-aware community engagement tracking, which can be cloned and adapted by any research community.

## About

The RCM-CRM is an open-source Community Relationship Management (CRM) system for Research Community Managers (RCMs), built by RCM Cooperative.

**Learn more about why we believe a CRM is appropriate tooling to manage community data in [this rational](docs/why-crm.md) and [this presentation](https://zenodo.org/records/23681028).**

### How to use

If you are interested in deploying this CRM for your community, start with the step-by-step [training documentation](docs/baserow/training/):
1. [Designing the visualisation](docs/baserow/training/01-designing-the-visualisation.md)
2. [Entering data](docs/baserow/training/02-entering-data.md)
3. [Maintinaing your data](docs/baserow/training/03-maintaining-your-data.md)
4. [Enabling self-serve editing](docs/baserow/training/04-enabling-self-serve-editing.md)
5. [Downloading your data](docs/baserow/training/05-downloading-your-data.md)
6. [Managing your visualisation](docs/baserow/training/06-managing-the-visualisation.md)

### Architecture

The current architecture uses Baserow - an open source database design tool with servers hosted in Germany — see the [architecture overview](docs/baserow/architecture-overview.md) and [Baserow schema](docs/baserow/schema.md) for the full design. An earlier self-hosted SQL/SQLite design remains documented as an alternative for deployments needing full infrastructure control (see [documentation on self-hosted architecture](docs/self-hosted-architecture/). A full [rationale for the current platform choice is available here](docs/platform-needs-assessment.md).

This tooling replaces a prior SharePoint-based MVP — the [RCM Cooperative Community Mapping Workflow](https://zenodo.org/records/15320348) — retaining [Kumu](https://kumu.io/) as the public-facing visualisation layer.

This tooling is designed to be cloned and handed off to individual community managers, via Baserow's own workspace export/import mechanism — see [Chapter 2: Entering data](docs/baserow/training/02-entering-data.md) in the training documentation for the confirmed process. RCM Cooperative are also pleased to support clients with customisation and data ingress/maintanance processes. Please [Contact us](https://www.rcmcooperative.com#contact) to discuss your needs. 

### Data privacy and protection

The data held in this CRM may cover both facts about your members (for example names, email addresses, ORCID, engagement data) and 'opinions' such as their relative influence and interest in your project. As such it is appropriate to manage this data with a high regard for the privacy of your members and security of access. 

We propose the following principles for how this data should be handled:
1. Data should be held in accordance with UK GDPR and the privacy policy of your hosting organisation.
2. Engagement data should be compiled from public sources (for example, public GitHub repositories) and from sources your have legitimate access to through your own activities (for example, pre-existing email engagements, Slack workspaces, or event registrations). You should noe seek out or compile data about members from sources outside these categories.
3. Data subjects should be offered a choice of exposure levels to consent to:
    - 3.1. No data holding: minimal information retained to build a suppression list which blocks further processing
    - 3.2. No external visibility: data used for internal monitoring only
    - 3.3. Aggregate or anonymised external visibility: publication of summary statistics incorporating this member, with no identifiable detail
    - 3.4. Pseudonymised external visibility: external publication of member engagement, connections, with identifiable information pseudonymised and linkage keys retained internally
    - 3.5. Full external visibility: external publication of member engagement, connections, and individual identifiable information. Note this tier is explicitly developed to make it easier for peers to find your expertise, and for you to connect with collaborators, other experts, and opportunities tailored to your interests. 
4. Opinions about the data subject (for example their level of interest or influence) should never be published.
5. Where internal data holding is consented to, that data should be visible by default to a small named group with operational responsibility (for example the delivery team assessing membership criteria and community health).
6. Any assessment of whether a member has met predefined engagement criteria (for example using the [Mountain of Engagement model](docs/engagement-framework.md) or RCM Cooperative membership requirements) should be treated as a suggestion for human review, not an automatic determination. 
7. Members should periodically be asked to review and validate our data holdings and (re)consent at their desired level
8. Members should be able to access and review their own recorded engagement data at any time, and raise a query or correction. 
9. Members should be able to request removal of their data, in line with data protection rights to erasure.
10. Data should not be shared with third parties outside the tool suppliers engaged, and only after thorough review of those suppliers' data privacy and security arrangements, including confirmation of where data is hosted and who (including any sub-processors) may access it.
11. AI/LLM tools may be used to help extract and structure engagement data from source material (for example, summarising meeting notes), but only on non-confidential material, and only using tools where data-training and retention policies have been explicitly reviewed. 
12. AI/LLM tools should not be used on any identifiable data, for example to identify or match members' records, flag duplicates, or make any determination about an individual's data (including membership criteria assessments) — this kind of processing is done using deterministic, non-AI methods, so that these decisions remain explainable and auditable. 
13. All documentation about the deployment should be made available to the community as the project progresses.
14. The community should be kept informed of the work and encouraged to contribute to the co-design of the tool, for example through discussions about what metadata it would be valuable to hold and communicate.

Further resources on our handling data privacy and protection in this tooling:
- [Data privacy comparison across considered architectures](docs/platform-needs-assessment.md#table-2-privacy-and-data-residency-comparison)
- [Data Privacy and Impact Assessment template materials](docs/data-privacy-assessment.md)
- The [Participant Information Sheet](https://github.com/uk-tre/community-management/blob/main/community-mapping/docs/UK-TRE-map-participant-information-sheet.md) developed to consent members for mapping of the UK TRE community. Note this deployment was customised to ensure all personal identifiable data was held in Microsoft Sharepoint until participants had consented to be publicy identifiable.

## The Team

This project is being developed and maintained by [RCM Cooperative](https://www.rcmcooperative.com/) (Co-Founders below). 

| Name | Affiliation | ORCID | GitHub |
| --- | --- | --- | --- |
| Cassandra Gould van Praag | RCM Cooperative | [0000-0002-8584-4637](https://orcid.org/0000-0002-8584-4637) | [@cassgvp](https://github.com/cassgvp) |
| Emma Karoune | RCM Cooperative; Alan Turing Institute | [0000-0002-6576-6053](https://orcid.org/0000-0002-6576-6053) | [@EKaroune](https://github.com/EKaroune) |
| Malvika Sharan | RCM Cooperative; St Jude Children's Research Hospital | [0000-0001-6619-7369](https://orcid.org/0000-0001-6619-7369) | [@malvikasharan](https://github.com/malvikasharan) |

**We welcome contributions from anyone interested in this topic, to help make this tool more robust and reproducible (see [CONTRIBUTING](#contributing)).**

See the full list of [Contributors](#contributors-) below. 

## AI Use

Some materials in this repository — including the drafting and editing of the step-by-step training documentation in `docs/baserow/training/` — were prepared with the assistance of Claude (Anthropic), used interactively by a human author who directed, reviewed, and edited the output rather than publishing it unread.

This is separate from the AI use inside the CRM's own skills (see [Repository structure](#repository-structure) below): those are marked explicitly as **\[uses an LLM\]** or **\[deterministic code, no LLM\]** per skill, reflecting whether live CRM data is ever exposed to a model — a distinct question from whether AI assistance was used to help write documentation *about* the CRM.

Confirm the exact wording and scope of this disclaimer against RCM Cooperative's own AI-use policy, if and when one exists, before treating this as final.

## Roadmap & Milestones

### v1 — Baserow build

This is a high-level overview of development. See also our [open issues](https://github.com/rcmcooperative/rcm-crm/issues) for specific activities or changes.

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

**Self-serve** (consent, re-confirmation, correction, addition via pre-populated row link)

- [x] Baserow's native Edit row link field generates unique per-row URLs that can be sent privately, pre-filled with the row's current data
- [ ] Tracking when self-serve validation has been provided
- [ ] Time-based signalling of review and consent

**Publishing and templating**

- [x] Public database template — workspace export/import confirmed working, including on Baserow's Free tier
- [x] Public data map (Kumu) — via the `crm-kumu-visualisation` pipeline above, individuals appear at their given consent level (excluded, pseudonymised, or identifiable)

**Documentation**

- [x] Step-by-step training documentation (`docs/baserow/training/`, six chapters) — Chapters 1–5 complete; Chapter 6 (Managing the visualisation) in progress
- [ ] Reproducible deployment write-up, CC-BY 4.0/MIT materials on GitHub (this repository)

### v1.1+ / v2

- [ ] Self-hosted Baserow deployment option, for clients where the third-party-processor relationship in `docs/platform-needs-assessment.md` (Table 2) is a blocker — see `docs/baserow/self-hosted-vs-cloud.md`
- [ ] Reporting via version-controlled Jupyter notebooks, pseudonymised IDs only, read-only DB connection, including aggregate summary statistics

- [ ] Email marketing/comms tooling integration (e.g. Mailchimp, Yet Another Mail Merge)
- [ ] NLP/chatbot-based contact entry
- [ ] Photo/name-tag OCR entry (vision-capable local model)
- [ ] Federated cross-community data exchange
- [ ] Reusable/API-driven duplicate-detection automation
- [ ] MOE (Mountain of Engagement) stage tracking and visualisation in Baserow itself — the conceptual framework is documented (`docs/engagement-framework.md`, currently marked for review) but not yet implemented as live Baserow fields/views
- [ ] Stalled/at-risk flagging (no recent interaction) — conceptually descriptive-only by design (see `docs/why-crm.md`), not yet implemented in Baserow
- [ ] Tagging/segmentation, with optional local-model-suggested tags based on interaction content
- [ ] Communication log (outreach sent, separate from interactions received)

**Web App** (data ingest UI, dashboard, mailing list integration — distinct from the Kumu export pipeline above, which is already built)

- [ ] Not yet built — see `docs/baserow/architecture-overview.md`



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

If you use or build on the RCM-CRM, please cite it as:

> Gould van Praag, C., Karoune, E., & Sharan, M. (2026). RCM-CRM (v1.0.0). RCM Cooperative. Zenodo. https://doi.org/10.5281/zenodo.23692251

Citation metadata is also available in [`CITATION.cff`](CITATION.cff).
GitHub's "Cite this repository" button (in the sidebar) will generate APA and BibTeX versions from it.


This project builds on the [RCM Cooperative Community Mapping Workflow](https://github.com/rcmcooperative/community-mapping):

> Gould van Praag, C. (2025). RCM Cooperative Community Mapping Workflow (v1.0.0). Zenodo. [https://doi.org/10.5281/zenodo.15320348](https://doi.org/10.5281/zenodo.15320348)

This repository builds on the template created and maintained by *The Turing Way* team members and shared under CC-BY 4.0 for reuse: [https://github.com/alan-turing-institute/reproducible-project-template](https://github.com/alan-turing-institute/reproducible-project-template).


## Contact

Reach out to [Cassandra Gould van Praag](https://github.com/cassgvp) at [cassandra.gouldvanpraag@rcmcooperative.com](mailto:cassandra.gouldvanpraag@rcmcooperative.com) with questions, feedback, or ideas.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/cassgvp"><img src="https://avatars.githubusercontent.com/u/43407869?v=4?s=100" width="100px;" alt="Cassandra Gould van Praag"/><br /><sub><b>Cassandra Gould van Praag</b></sub></a><br /><a href="https://github.com/rcmcooperative/rcm-crm/commits?author=cassgvp" title="Code">💻</a> <a href="https://github.com/rcmcooperative/rcm-crm/commits?author=cassgvp" title="Documentation">📖</a> <a href="#ideas-cassgvp" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.turing.ac.uk/people/research-associates/emma-karoune"><img src="https://avatars.githubusercontent.com/u/58147174?v=4?s=100" width="100px;" alt="Emma Karoune"/><br /><sub><b>Emma Karoune</b></sub></a><br /><a href="#ideas-EKaroune" title="Ideas, Planning, & Feedback">🤔</a> <a href="https://github.com/rcmcooperative/rcm-crm/commits?author=EKaroune" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://malvikasharan.github.io/"><img src="https://avatars.githubusercontent.com/u/5370471?v=4?s=100" width="100px;" alt="Malvika Sharan"/><br /><sub><b>Malvika Sharan</b></sub></a><br /><a href="#ideas-malvikasharan" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/MarySHADE"><img src="https://avatars.githubusercontent.com/u/159810285?v=4?s=100" width="100px;" alt="MarySHADE"/><br /><sub><b>MarySHADE</b></sub></a><br /><a href="#ideas-MarySHADE" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

See [All-Contributors bot usage](https://allcontributors.org/en/bot/usage/) for how to add contributors to this repo. 

## Checklist for setting an online repository

This repo has been templated from the [RCM Cooperative Partner template repo](https://github.com/rcmcooperative/partner-template), including file structure, starter contents and a Claude Skill to fill in template information.

This repo includes:

- [x] A meaningful and accurate README.md
- [x] A meaningful and accurate [CONTRIBUTING](CONTRIBUTING.md) file
- [x] A [LICENSE](LICENSE.md) (we suggest MIT for code and CC-BY-4.0 for documentation)
- [x] A [Code of Conduct](CODE_OF_CONDUCT.md) (we suggest RCM Cooperative CoC)
- [x] A directory for project management (communications, meetings, reports, proposals)
- [x] A directory for assets (non-code supporting files such as images, diagrams, templates, and similar media) that are used in the projects documentation or output)
- [x] A directory for documentation
- [x] Ready to use [all-contributors](https://allcontributors.org/) bot (installed for the RCM Cooperative GitHub organisation)
- [x] Appropriate issue templates
- [x] Appropriate .gitignore file
- [x] Connect repo with Zenodo the order of these needs to be reviewed
- [x] Add cff file for citation (we suggest creating this with [https://bit.ly/cffinit](https://bit.ly/cffinit))
- [x] Add a DOI badge (see the zenodo doi badge widget)