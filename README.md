# RCM CRM
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

## About this Repository

This repository contains the documentation, research materials, and outputs for the **RCM-CRM project**, developed by the [RCM Cooperative](http://rcmcooperative.com/).

This project follows open research principles to deliver FAIR and openly licensed materials. 
Publication of these materials supports transparency in this project, and reproducibility of similar work. 
All materials from the project are published as open as possible, as closed as necessary.

This repository builds on the template created and maintained by *The Turing Way* team members and shared under CC-BY 4.0 for reuse: https://github.com/alan-turing-institute/reproducible-project-template.

When reusing this repository, you can run the Claude skill /update-template-repo (included here) to update the information below with information relevant to the project.

Note after templating this directory, you may wish to create an additional directory called `private`. 
Use this directory to enable files to be stored locally without being included in the main repo (this directory is excluded by the [.gitignore](~/.gitignore)). 
This is useful where there are restrictions on sharing some information (GDPR) or license terms are yet to be agreed. 

## Vision and Mission

- **Vision:** Research community managers everywhere have open, privacy-conscious, ethical tools for understanding and growing their communities.
- **Mission:** To build and maintain a self-hosted, open-source CRM for Research Community Managers (RCMs), enabling transparent, GDPR-aware community engagement tracking — designed to be cloned and adapted by any research community.

## About

The RCM-CRM is a self-hosted, open-source Customer Relationship Management (CRM) system for Research Community Managers (RCMs), built by the RCM Cooperative.

It replaces a prior SharePoint-based MVP — the [RCM Cooperative Community Mapping Workflow](https://github.com/rcmcooperative/community-mapping) — retaining [Kumu](https://kumu.io/) as the public-facing visualisation layer.

Designed from the outset to be cloned and handed off to individual client communities, with client-specific configuration layered on top of a common template.

## Roadmap & Milestones

### v1

- [ ] SQLite database with generic relationship and custom-field model
- [ ] MOE (Mountain of Engagement) stage tracking with full stage-history audit trail
- [ ] Automated stage-progression suggestions (RCM confirms, not auto-applied)
- [ ] Mountain-shaped visualisation (scaled parallelograms per stage) and kanban board view
- [ ] Stalled/at-risk flagging (no recent interaction)
- [ ] Tagging and segmentation, with optional local-Qwen-suggested tags based on interaction content
- [ ] Duplicate-contact detection across multi-source intake
- [ ] Communication log (outreach sent, separate from interactions received)
- [ ] Reporting via version-controlled Jupyter notebooks with pseudonymised IDs only
- [ ] Email pipeline integration (Gmail API + local Qwen3 via Ollama) surfacing matched engagement activities
- [ ] Docker-based self-hosted deployment

### v1.1+ / v2

- [ ] ORCID OAuth and token-based self-service correction form
- [ ] Email marketing/comms tooling integration (e.g. Mailchimp, Yet Another Mail Merge)
- [ ] NLP/chatbot-based contact entry
- [ ] Photo/name-tag OCR entry (vision-capable local model)
- [ ] Federated cross-community data exchange
- [ ] Migration path from SQLite to Postgres for concurrent multi-user editing

## The Team

| Name | Affiliation | ORCID | GitHub |
|---|---|---|---|
| Cassandra Gould van Praag | RCM Cooperative | [0000-0002-8584-4637](https://orcid.org/0000-0002-8584-4637) | [@cassgvp](https://github.com/cassgvp) |
| Emma Karoune | RCM Cooperative | [0000-0002-6576-6053](https://orcid.org/0000-0002-6576-6053) | [@EKaroune](https://github.com/EKaroune) |
| Malvika Sharan | St Jude Children's Research Hospital | [0000-0001-6619-7369](https://orcid.org/0000-0001-6619-7369) | [@malvikasharan](https://github.com/malvikasharan) |

## Contributing

- **Guidelines:** [Contribution Guidelines](CONTRIBUTING.md) for contributors.
- **Code of Conduct:** [Code of Conduct](CODE_OF_CONDUCT.md) ensures a respectful project environment.

## Licensing

This project is licensed under the CC-BY-4.0 License for documentation and MIT license for code - see the LICENSE.md file for details.

## Citing & Acknowledgement

This project builds on the [RCM Cooperative Community Mapping Workflow](https://github.com/rcmcooperative/community-mapping):

> Gould van Praag, C. (2025). RCM Cooperative Community Mapping Workflow (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.15320348

To cite this repository, please use the information in [`CITATION.cff`](CITATION.cff) once it has been added — see the setup checklist below.

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
      <td align="center" valign="top" width="14.28%"><a href="https://www.turing.ac.uk/people/research-associates/emma-karoune"><img src="https://avatars.githubusercontent.com/u/58147174?v=4?s=100" width="100px;" alt="Emma Karoune"/><br /><sub><b>Emma Karoune</b></sub></a><br /><a href="#ideas-EKaroune" title="Ideas, Planning, & Feedback">🤔</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://malvikasharan.github.io/"><img src="https://avatars.githubusercontent.com/u/5370471?v=4?s=100" width="100px;" alt="Malvika Sharan"/><br /><sub><b>Malvika Sharan</b></sub></a><br /><a href="#ideas-malvikasharan" title="Ideas, Planning, & Feedback">🤔</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

Note we are currently using locally installed all-contributors while this repo is private. 
Add contributors locally using the below command in a terminal then push changes.

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
- [ ] Connect repo with Zenodo <mark>the order of these needs to be reviewed</mark>
- [ ] Add cff file for citation (we suggest creating this with https://bit.ly/cffinit)
- [ ] Add a DOI badge (see the zenodo doi badge widget)








