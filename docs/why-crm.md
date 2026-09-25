# A CRM for Research Community Managers

## Executive summary

Research Community Managers hold detailed, valuable knowledge about the people in their communities, such as who is involved, how, and where influence and momentum lie. 
This knowledge is usually informal and lost when project delivery teams change. 
The RCM-CRM makes this knowledge explicit, shared, and durable, turning this essential data curation into a reproducible workflow rather than a one-off activity, and into a visible asset that benefits funders as much as the community manager themselves.

This matters beyond internal efficiency. Existing community metrics are coarse and rarely map well onto research communities, leaving funders with little reliable evidence for their investment in community infrastructure. 
The act of measuring engagement well introduces its own ethical risks, from surveillance concerns to Goodhart's Law. 
The RCM-CRM is deliberately designed around this tension rather than in spite of it, drawing on ongoing, funded, peer-recognised work on ethical community intelligence.

Where useful, the RCM-CRM borrows concepts from commercial CRMs and sales pipelines — stage tracking, prioritisation by influence and interest — but only once decoupled from a sales pipeline's goal of conversion, as community members are not 'leads', and engagement is not something to be indefinitely maximised. 
MBecause this involves identifiable data about community members, deployment falls under UK GDPR, and institutions should consult their Data Privacy Officer before installing the RCM-CRM; see the accompanying [data privacy documentation](data-privacy.md).

## Managing a community means knowing your members

Research Community Managers (RCMs) design for people.
To do that well, we need to know who those people are so we can anticipate and respond to their needs, understand who is supporting and has influence, design inclusively, know who to speak to when, and know who to connect to whom.

This type of knowledge has historically been implicit and informal (held in someone's head, in a scattered set of spreadsheets, or spread across multiple separate tools) and sometimes lost entirely when a community manager moves on.
A Customer Relationship Management system (CRM) makes this knowledge explicit, shared, and durable.

A CRM also makes this information robust, and aligns our practice with the standards expected for transparent and reproducible data science. The RCM-CRM is therefore intended to be a transparent and reproducible workflow for RCMs, enabling ongoing analysis and communication about the efficacy of engagement efforts. It is intended to be incorporated as a value-adding cornerstone activity in the RCMs practice, not just a one-off activity. 

The data handled within the RCM-CRM includes identifiable records about our community members and as such falls under (UK) GDPR provisions. It is managed by the CRM in line with the transparency principles of "as open as possible, as closed as necessary". **Before installing RCM-CRM for your community, please discuss the tooling with your Data Privacy Officer.** Information relevant to your institutional Data Privacy Impact Assessment (DPIA) is shared in  the [data privacy documentation](data-privacy.md)

## Visibility as a shared asset, not just a management tool

The value of this knowledge isn't limited to the community manager who holds it.
Made visible (subject to consent), the same map that helps an RCM manage a community also helps community members themselves to seeing where they sit within the community and identifying potential collaborators they might not otherwise have found.
This transfers knowledge that would otherwise be held by one person into a shared asset available to the whole community.

The resulting visualisation is also a valuable communication tool in its own right.
A network map or engagement view makes implicit, hard-to-articulate knowledge about a community's shape and connections immediately visible to external audiences (for example funders, partner organisations, or prospective collaborators) in a way that a written description alone struggles to convey.

## Why funders should care

### Existing metrics are too coarse

RCMs typically rely on simple counts (for example mailing list size, Slack member numbers, event attendance) to describe the health of a community.
These metrics are coarse, lag behind real changes in engagement, and miss the factors that actually determine whether a community is sustainable.
Existing shared metrics frameworks, such as those developed for open-source or commercial communities (for example, CHAOSS), don't map cleanly onto research communities either, because research communities have different motivations and different normalised ways of working compared to open-source software developers.

Without better metrics, funders investing in the "socio-technical infrastructure" of collaboration — communities, networks, and the people who manage them — have no reliable way to know whether that investment is working, beyond anecdote or a headline member count.
The structured, multi-source record of engagement which the CRM produces gives funders a genuinely usable evidence base for that investment.

### The measurement problem is also an ethical problem

Better metrics create a genuine risk alongside the opportunity: once community engagement is measured, there is a temptation to treat the metric itself as the goal (Goodhart's Law), and a real risk that people feel surveilled rather than supported, which can chill the very engagement the metric was meant to capture.

This topic is the explicit subject of an SSI (Software Sustainability Institute) Fellowship awarded to RCM Cooperative's Executive Director, Cassandra Gould van Praag: ["Conversations on ethical community intelligence"](https://www.software.ac.uk/news/introducing-2026-fellowship-cohort-insights-and-celebrations), 2026 cohort.
The fellowship is organised around four core concerns that this CRM's design directly reflects: informed consent, the behavioural impact of surveillance, the risk of misuse, and Goodhart's Law. 
The fellowship also brings together RCMs and contributors to existing community metrics projects (including CHAOSS) to work toward a common language and shared, ethical methodology for measuring research community health.

### What this means for the CRM's design

This CRM is built to take the funder-motivation case seriously with regard to the ethical concerns of surveillance-style monitoring.
Engagement scoring is descriptive rather than a target to be maximised (avoiding the Goodhart's Law trap by design). The consent model is explicit and reviewable, and ethical grounding is the subject of ongoing, funded, peer-recognised work.
For a funder, this means the same underlying data that demonstrates the value of their investment in community infrastructure is collected in a way that protects the the community that infrastructure depends on.

## Why this needs tooling, not just goodwill

Research communities increasingly communicate across many channels: Slack, Discourse, email, GitHub, conference talks, mailing lists.
This creates two problems.

First, individual community managers face information overload trying to track activity across all of these channels for even a single community.

Second, without an ecosystem-level view, we get a biased picture of community priorities and interests, limited by whoever happens to be paying attention to which channel.
Critical signals such as a recurring concern, a growing interest, a person quietly becoming a leader, can go unnoticed simply because no one was tracking the right channel at the right time.

This is the coordination failure a CRM is built to address, by making the record of that relationship-building visible, structured, and shared across a team.

## The sales-pipeline analogy, and where it breaks down

Commercial CRMs are built around a sales pipeline: a prospect moves through defined stages (lead, qualified, negotiation, closed) toward a single goal, a sale.
Community engagement has a structurally similar shape (see `engagement-framework.md`) and has a comparable progression, from first contact through to community leadership.

The analogy is useful because it identifies underlying tools used to manage the sales pipeline which can be repurposed for community management, for example stage tracking, a visual pipeline, and flags for people who have stalled.

The analogy breaks down, however, as sales pipelines and community sustainability are optimised for different things. 
A sales pipeline optimises for conversion — moving as many prospects as possible toward a sale, as efficiently as possible.
Community engagement, however, is not a conversion funnel, and people are not leads.
Progression up the Mountain of Engagement is not the goal in itself; it is a signal a community manager uses to understand and support people, not a target to be maximised.
The CRM tracks engagement level as a fact worth knowing, not a KPI to be driven upward for its own sake.

This distinction shapes several design decisions in the CRM: engagement scoring is descriptive, not prescriptive; stalled-contact flagging surfaces a fact for human judgement rather than triggering automated outreach; and the tool deliberately avoids any framing that could make community members feel monitored or optimised against, rather than supported.

## Prioritising engagement

Not all relationships need the same attention.
Understanding a person's influence over a programme, and their interest in it, helps prioritise engagement effort:

- **Keep informed** — disseminate updates at an appropriate level
- **Keep satisfied** — high influence, lower interest
- **Manage closely** — high influence, high interest
- **Monitor** — follow activity to anticipate needs

This influence/interest framework, alongside the Mountain of Engagement, forms the conceptual backbone of how the CRM organises and prioritises community relationships.
See `engagement-framework.md` for the full detail.

## A note on language

The term ["stakeholder" has a colonial history](https://blogs.lse.ac.uk/impactofsocialsciences/2024/05/07/should-we-stop-using-the-word-stakeholder-in-research/).
Where possible, we name groups explicitly, or use alternative language such as "interest holders."
This document and the CRM's design follow that convention.

## Summary: Why we built this ourselves

This CRM exists because a research community's knowledge of its own members shouldn't depend on one person's memory.
The tooling itself addresses the scaling issue of measurement of engagement across many channels and a growing community, and provide a sophisticated and nuanced analysis of engagement which could provide valuable funder insight. 
Making this knowledge explicit and durable also makes it a shared asset, with the resulting visualisation giving both funders and community member a clear, honest picture of a community that words alone struggle to convey.

The sales-pipeline concepts it borrows from are useful, but only once decoupled from a sales pipeline goal of conversion, since people are not leads and engagement is not something to be maximised indefinitely.
Aligned with this shift in purpose, we acknowledge that the development of automated measurements brings real ethical risk which must be carefully managed in order to maintain the trust of our communities, and have designed the RCM-CRM to both mitigate and stimulate discussions around these risks. 

No existing CRM tool was built for this specific texture and interests of a research community as described above. Building our own let us design for that from the start, and share this infrastructure as a cornerstone to reproducible RCM workflows which could significantly accelerate the professionalism and efficacy of RCM activities across the ecosystem. 

