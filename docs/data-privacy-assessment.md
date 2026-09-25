# RCM-CRM — Data Protection Impact Assessment (Generic Template)

This is a generic Data Privacy Impact Assessment (DPIA) template for RCM-CRM deployments, adapted from the data protection assessment completed for the original community-mapping MVP (TRIC-DT and Environment and Sustainability Communities, Alan Turing Institute, December 2023).
It is intended to be copied and completed per deployment (RCM Cooperative's own instance, or a client instance), not used as-is.
Sections marked `<...>` need deployment-specific completion.

<mark>Sections and passages highlighted were not part of the original MVP's data protection assessment. They reflect new considerations arising from how the RCM-CRM has evolved since as a self-hosted, multi-client architecture with planned local-AI features. These sections should be treated as unresolved and further investigated for DPIA relevant details.</mark>

## Part 1: General information

| | |
|---|---|
| Project/activity name | `<deployment name>` |
| Data owner/completing this assessment | `<name>` |
| Date completed | `<date>` |
| Description of activity | Collating and managing data about individuals (name, email, affiliations, engagement activity), organisations, and projects connected to `<community name>`, to support community engagement, and producing a visualisation of these connections. |
| <mark>Data retention period</mark> | <mark>`<Insert retention period or review trigger>`. The original MVP's assessment did not specify a retention period, deferring instead to an institutional policy that no longer applies in a self-hosted, multi-client model. This must be explicitly defined per deployment, not left implicit.</mark> |

## Part 2: Describe the data processing

### Source of data
Data will be drawn from a mix of sources depending on deployment configuration: public-domain information (institutional profiles, project pages, publications), direct contact/sign-up (mailing list, event registration), and records of participation in community activities (events, Slack, GitHub, mailing lists).

### Data categories processed
- Names
- Email addresses
- Affiliations (to projects, institutions, companies, or working groups)
- Connections between individuals based on shared affiliations
- Records of engagement (participation in events, community fora, contributions)
- Inferred/assessed engagement level (Mountain of Engagement stage)
- Inferred/assessed influence and interest level over the programme
- Recommended engagement approach (e.g. keep informed / keep satisfied / manage closely / monitor)

None of the above constitutes special category data by default.
`<Confirm per deployment: are any special category data — race, ethnicity, political opinion, religion, trade union membership, genetic/biometric data, health, sex life/orientation — being collected? This should not be the case for a standard deployment; flag and escalate if it arises.>`

### Estimated volume
`<Insert expected number of contacts, e.g. "approximately 200 initially, growing to 500–1000">`

### Data subjects
`<Describe who is included, e.g. project team members, contributors, partner organisation staff, self-nominated community members>`

### Who the data is shared with
`<Describe: internal team only? Client organisation? Public (with consent)? Any third-party processors, e.g. cloud AI providers?>`

For deployments using Baserow Cloud (RCM Cooperative's own CRM, and any future deployment that follows the same platform choice — see `platform-needs-assessment.md`), Baserow acts as a third-party data processor. Confirm current status of the DPA, TOM, and international-transfer safeguards against `platform-needs-assessment.md`, Table 2, before treating this as resolved for a given deployment.

<mark>Where RCM Cooperative builds and hands off a CRM instance to a client, the controller/processor relationship needs explicit clarification per engagement — for example, whether RCM Cooperative acts as a processor during build, with the client becoming the controller thereafter.</mark>

## Part 3: Context and purpose

### Is this processing for research or operational work?
Typically operational (community management), not a research project in itself, unless the deployment is explicitly research-labelled.
`<Confirm per deployment>`

### Would individuals expect this processing?
Community/stakeholder mapping is an increasingly standard part of professional community management.
Individuals with a direct relationship to the community (e.g. mailing list members, event attendees) are more likely to expect this than individuals identified solely through public-domain research.

### Purpose

This deployment aims to give the community management team a shared, structured record of who is involved in the community and how, replacing informal knowledge held by individuals. This supports more consistent engagement (knowing who to contact, when, and about what), earlier identification of people who could take on greater involvement or leadership, and clearer reporting to funders and partner organisations on community health and engagement outcomes over time. Processing is limited to what is needed for these purposes; it is not used to make automated decisions about individuals, and engagement data is not used to rank, target, or exclude people.

### Benefits

This processing benefits the organisation by reducing reliance on one person's memory or a scattered set of spreadsheets, so community knowledge survives staff changes and is shared consistently across the team. It benefits community members by supporting more timely, relevant engagement — for example, noticing when someone might welcome an introduction, an opportunity, or a greater role, rather than this depending on chance. It benefits funders and partner organisations by making it possible to report on community engagement and health with structured evidence, rather than coarse proxies such as raw membership counts, which lag behind and obscure real changes in community sustainability. More broadly, this work contributes to the wider professionalisation of research community management as a discipline, and to the development of ethical, standardised community health metrics for the research sector.

<mark>The federated cross-community data exchange model explored in the unsuccessful Astera Open Science Fellowship application — sharing summarised signals across separate community deployments — was never assessed here. This should have its own dedicated DPIA if and when federation moves from "design should leave room for it" to an actual built feature; it is a materially different risk profile to anything else in this document.</mark>

## Part 4: Lawful basis, necessity, and proportionality

### Lawful basis
Legitimate interests is the anticipated lawful basis for most deployments, following the same three-part test used in the original assessment:
1. **Identify the interest** — `<RCM Cooperative (or the relevant deploying organisation)>` has a legitimate interest in effective community management and reporting: maintaining a structured, shared record of who is involved in a research community, how they are engaged, and how that engagement changes over time. This supports the practical delivery of community management activities (facilitating collaboration, identifying engagement opportunities, and providing continuity when staff change), and supports transparent reporting to funders and partner organisations on community health and the outcomes of engagement work. This interest is limited to community management and reporting purposes; it does not extend to marketing, profiling for commercial gain, or any use beyond supporting the community itself.
2. **Necessity** — The processing is necessary for this interest. Effective community management requires knowing who is involved and how, which by definition requires processing personal data (names, contact details, affiliations, and records of engagement); this cannot meaningfully be done using anonymised or aggregate data alone, since the purpose depends on recognising and engaging with specific individuals over time. The processing is limited to the minimum needed for this purpose: core identifying and affiliation data, plus records of engagement activity directly relevant to community management and reporting. Optional or additional fields are enabled only where a specific deployment has a genuine need for them, rather than collected by default (see the CRM's generic, extensible field design in `architecture-technical.md`).
3. **Balancing** — The impact on individuals is limited and proportionate to the interest. The personal data processed is largely low-sensitivity (name, email, professional affiliation, and engagement records), rather than special category data. Individuals with an existing relationship to the community (for example, through a mailing list, event registration, or direct contact) can reasonably expect this kind of processing as part of standard community management practice. Individuals are given a choice over their visibility (identifiable, pseudonymised, or excluded — see the consent/privacy tiers above), and internal engagement assessments are not made public without explicit agreement. Given these safeguards, the benefit of effective, well-evidenced community management is not considered to be overridden by the impact on individuals. Where a specific deployment involves individuals who are vulnerable, under 18, or where data is more sensitive than the default case, this balancing test must be redone explicitly rather than assumed to hold.

`<Confirm per deployment whether legitimate interests applies, or whether consent or another lawful basis is more appropriate — e.g. where a client's own governance requires consent-based processing.>`

### Necessity and data minimisation
The generic RCM-CRM schema is designed to support minimisation by default: fields are opt-in and extensible (see `architecture-technical.md`), rather than a fixed schema collecting maximal data regardless of relevance.
`<Confirm per deployment that only fields genuinely necessary for that community's engagement purpose are enabled.>`

### Consent and privacy tiers
Individuals represented in the data should be offered a choice over their visibility, for example:
1. **Publicly identifiable** — appears with identifying information on any public output
2. **Publicly pseudonymised** — appears without identifying information, retaining only affiliations/connections
3. **Not included** — no data included in any public output

Internal engagement/influence assessments ("opinions") are not made public regardless of tier, unless explicit agreement is given.
This maps to the CRM's `internal_visible` / `external_consent` fields (see `architecture-technical.md`).

<mark>The original assessment allowed individuals to correct factual data and opt out of public sharing, but had no review or correction mechanism for internally-held "opinion" data (engagement/influence assessments). This connects directly to the CRM's own deferred v2 self-service correction form — worth deciding explicitly whether that mechanism should extend to opinion/scoring data, not just factual fields, when it is built.</mark>

## Part 5: AI-specific considerations

<mark>This entire section was not present in the original MVP's assessment, since the MVP involved no AI component. Where a deployment uses AI/ML components (for example, a local LLM generating interaction summaries or suggesting tags), the following must be considered and documented. This is untested territory rather than a like-for-like carryover from the original assessment, and should be reviewed with particular care.</mark>

- Assess potential statistical inaccuracies, unfair bias, or discrimination in the system's output, and identify mitigations
- Ensure only data relevant to the stated purpose is used to inform any AI-generated suggestion
- Ensure AI-generated suggestions (tags, summaries, engagement-stage suggestions) are reviewed and confirmed by a human, not applied automatically
- Document minimum success criteria or review points before relying on AI-generated output operationally
- Consider whether the data used reflects or risks reproducing past discrimination or unequal representation (see the bias considerations in `engagement-framework.md`)

<mark>If any deployment uses a cloud-based AI provider (as opposed to fully local inference) for any part of processing, this introduces an international data transfer question the original, fully-local, single-institution assessment never had to consider. This should be flagged explicitly, deployment by deployment, rather than assumed away.</mark>

## Part 6: Risk assessment

| Risk | Likelihood | Severity | Overall risk | Mitigation |
|---|---|---|---|---|
| Data breach exposing engagement/influence assessments, leading to reputational damage | Possible | Minimal | Low | <mark>Maintain data on secured, access-controlled systems; limit access to relevant team members. The original assessment relied on "Turing approved data management systems" as this control. Where a deployment self-hosts (see `self-hosted-architecture/`), a per-client deployment has no equivalent central IT/security backstop, so this mitigation must be re-established explicitly, not assumed equivalent. Where a deployment uses Baserow Cloud instead, a vendor-provided security backstop does exist, but this introduces a different risk — reliance on a third-party processor's own security practices rather than controls RCM Cooperative sets directly. See `platform-needs-assessment.md`, Table 2, for the current state of DPA/TOM/SCC verification for this vendor relationship; this row should reference that table's findings rather than duplicate them, and should be updated once verification is complete.</mark> |
| Data breach exposing identifiers for individuals who have not agreed to public identification | Remote | Minimal | Low | Consent checks before any public output; pseudonymisation by default; data minimisation |
| `<Add deployment-specific risks>` | | | | |

## Part 7: Sign-off

| | |
|---|---|
| Measures approved by | `<name, date>` |
| Reviewed by (if applicable — e.g. client organisation's own data protection contact) | `<name, date>` |
| Date of next review | `<date>` |
