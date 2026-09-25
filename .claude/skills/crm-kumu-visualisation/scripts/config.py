"""
Schema registry for the CRM -> Kumu export pipeline.

This is the ONE file to edit when Baserow's schema changes (renamed/added
fields, new tables, new consent options, new edge types). pipeline.py itself
should not need editing for ordinary schema drift.

Conventions
-----------
- "Type" in Kumu = the source Baserow table name (Person / Organisation /
  Community / Project). Interactions are NOT imported as Kumu elements —
  per decision, they are flattened into a pipe-separated metadata list on
  whichever People/Organisations/Communities/Projects rows they touch.
- Every element gets an ID of the form "<Type>-<baserow row id>", which is
  globally unique across all five tables. This is what lets two same-labelled
  rows in different tables (e.g. "OLS" as both an Organisation and a
  Community) import as distinct Kumu elements, and it's also what the
  connections sheet's From/To columns reference (Kumu requires IDs in
  From/To once the elements sheet uses an ID column).
- Edge types are GENERIC (shared across tables) for now: lead, participant,
  contact, contributor, employee, sponsor, funder, child-of, affiliated.
  Per-table-pair-specific edge types (e.g. "project-lead" vs
  "community-lead") can be revisited later once the graph itself makes the
  Organisation/Community and Project/other-table boundaries clearer.
"""

# ---------------------------------------------------------------------------
# Node tables (become Kumu elements)
# ---------------------------------------------------------------------------

NODE_TABLES = {
    "Person": {
        "file_stub": "People",
        "id_field": "id",
        "label_field": "name-person",
        "size": 1,
        "consent_field": "mapping-consent",
    },
    "Organisation": {
        "file_stub": "Organisations",
        "id_field": "id",
        "label_field": "name-org",
        "size": 100,
        "consent_field": None,
    },
    "Community": {
        "file_stub": "Communities",
        "id_field": "id",
        "label_field": "name-community",
        "size": 50,
        "consent_field": None,
    },
    "Project": {
        "file_stub": "Projects",
        "id_field": "id",
        "label_field": "name-project",
        "size": 50,
        "consent_field": None,
    },
}

# Interactions are loaded (for schema validation / a future richer metadata
# pass) but are NOT turned into Kumu elements or edges directly. All the
# role-specific rollups we need (who led/participated/sponsored/funded which
# interaction) already exist as link fields on the four tables above
# (e.g. Person.interactions-lead, Organisation.interactions-sponsor), so we
# read the metadata from those columns rather than joining back to
# Interactions itself.
NON_NODE_TABLES = {
    "Interaction": {
        "file_stub": "Interactions",
    },
}

ALL_TABLE_STUBS = {**{k: v["file_stub"] for k, v in NODE_TABLES.items()},
                   **{k: v["file_stub"] for k, v in NON_NODE_TABLES.items()}}

# ---------------------------------------------------------------------------
# Expected columns per table, for schema-drift detection.
# Source: baserow-structure-json-<Table>.json field-definitions exports,
# most recently taken 2026-09-24. If Baserow's live schema changes, re-run
# the structure export and update this list -- the pipeline will raise a
# clear error on drift rather than silently mis-mapping columns.
#
# A handful of People fields (Baserow's Form-view helper "edit-row-link",
# plus the "-user-nominated" free-text fields -- orgs-user-nominated,
# communities-lead-user-nominated, communities-participant-user-nominated,
# pronouns-user-nominated, notes-user-nominated, socials-other-user-nominated,
# git-other-user-nominated) are listed here so the drift check recognises
# them, but are DELIBERATELY not carried into the Kumu export -- see the
# note above PROFILE_FIELDS below.
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = {
    "People": [
        "id", "name-person", "name-person-first", "email-1",
        "carrer-current-role-title", "organisations",
        "communities-contributor-profile", "interactions-lead",
        "name-person-last", "pronouns", "email-2", "notes", "github",
        "institutional-profile", "linkedin", "ORCID", "projects-contact",
        "career-stage", "mapping-consent", "interactions-participant",
        "Last modified", "Last modified by", "communities-lead",
        "projects-lead", "projects-contributors", "Created on", "Created by",
        "email-3", "communities-participant",
        "edit-row-link", "orgs-user-nominated",
        "communities-lead-user-nominated", "communities-participant-user-nominated",
        "pronouns-user-nominated", "notes-user-nominated",
        "socials-other-user-nominated", "git-other-user-nominated",
    ],
    "Organisations": [
        "id", "name-org", "people-employees", "type", "name-org-long",
        "name-org-abbreviation", "notes", "website", "last-modified-by",
        "last-modified-date", "communities-sponsor", "projects-sponsor",
        "projects-funder", "interactions-sponsor", "interactions-funder",
        "Created on", "Created by", "org-child-of",
    ],
    "Communities": [
        "id", "name-community", "description", "name-community-long",
        "name-community-abbreviation", "people-leads", "website",
        "organisations", "last-modified-by", "last-modified-date",
        "projects-sponsor", "interactions", "people-participants",
    ],
    "Projects": [
        "id", "name-project", "description", "date-start", "date-end",
        "status", "interactions", "people-contacts", "name-project-long",
        "name-project-abbreviation", "people-leads", "people-contributors",
        "github-issue", "notes", "org-sponsor", "org-funder", "communities",
        "website", "last-modified-by", "last-modified-date",
    ],
    "Interactions": [
        "id", "name-interaction", "status", "date-started", "notes",
        "people-leads", "projects", "people-participants",
        "name-interaction-long", "name-interaction-abbreviation", "type",
        "urls-outputs", "urls-internal", "date-delivered",
        "date-last-activity", "github-issue", "communities", "org-sponsor",
        "org-funder", "last-modified-date", "last-modified-by",
        "Created on", "Created by",
    ],
}

# ---------------------------------------------------------------------------
# Edge registry: one entry per link field that should become a Kumu
# connection. Only ONE side of each inverse pair is listed (the pair itself
# is noted in a comment) to avoid emitting duplicate edges.
#
# ASSUMPTIONS FLAGGED FOR REVIEW (edge_type == "affiliated"):
#   - Community.organisations has no equivalent generic field on the
#     Organisations side (Organisations only has the sponsor-specific
#     `communities-sponsor`), so it's kept as its own edge rather than
#     treated as an inverse of anything. It may end up overlapping with
#     `sponsor` edges for orgs that are both a general affiliate and a
#     sponsor of the same community -- worth checking once visualised.
#   - Project.communities is likewise kept as its own edge, distinct from
#     Community.projects-sponsor (Community -> Project, sponsor role).
# Both are labelled "affiliated" for now; happy to rename/fold these in
# once the graph makes the real relationship clearer.
# ---------------------------------------------------------------------------

EDGE_FIELDS = [
    # source_type, field name (on source table), target_type, edge type
    ("Person", "organisations", "Organisation", "employee"),
    # Organisation.people-employees is the inverse of the above -- skipped.
    ("Person", "communities-lead", "Community", "lead"),
    # Community.people-leads is the inverse of the above -- skipped.
    ("Person", "communities-participant", "Community", "participant"),
    # Community.people-participants is the inverse of the above -- skipped,
    # same as every other pair. Originally auto-named "People" by Baserow;
    # Cass renamed it to people-participants (2026-09-25), same field id
    # (11049878), same relationship -- cosmetic rename only, no logic change.
    ("Person", "projects-contact", "Project", "contact"),
    ("Person", "projects-lead", "Project", "lead"),
    ("Person", "projects-contributors", "Project", "contributor"),
    # Project.people-contacts / people-leads / people-contributors are the
    # inverses of the three rows above -- skipped.
    ("Organisation", "communities-sponsor", "Community", "sponsor"),
    ("Organisation", "projects-sponsor", "Project", "sponsor"),
    ("Organisation", "projects-funder", "Project", "funder"),
    # Project.org-sponsor / org-funder are the inverses of the two rows
    # above -- skipped.
    ("Organisation", "org-child-of", "Organisation", "child-of"),
    ("Community", "organisations", "Organisation", "affiliated"),  # see note above
    ("Community", "projects-sponsor", "Project", "sponsor"),
    ("Project", "communities", "Community", "affiliated"),  # see note above
]

# ---------------------------------------------------------------------------
# Metadata-only fields: Interaction-role rollups, kept as a pipe-separated
# list of interaction names on the node's profile, NOT turned into edges.
# ---------------------------------------------------------------------------

INTERACTION_METADATA_FIELDS = {
    "Person": ["interactions-lead", "interactions-participant"],
    "Organisation": ["interactions-sponsor", "interactions-funder"],
    "Community": ["interactions"],
    "Project": ["interactions"],
}

# ---------------------------------------------------------------------------
# Other descriptive metadata columns carried onto the elements sheet
# (beyond ID / Label / Type / Size / consent / interaction rollups).
# Collaborator-name and "boring" system columns are deliberately excluded,
# consistent with Cass's established sanitisation practice elsewhere in the
# CRM skills (never surface "Last modified by" / "Created by" names).
#
# NOT carried through, on purpose: People's seven "-user-nominated" fields
# (populated by a public self-nomination form Cass built in Baserow) and
# "edit-row-link" (a Baserow form-view UI helper, not data). Per the
# authoritative policy Cass wrote for the content-extraction skill that
# writes to these fields (latest version: the "provenance principle" doc,
# confirmed 2026-09-24), the seven fields exist because a human typed them
# into that self-nomination form -- their defining property is PROVENANCE
# (came from a person's own self-report), not topic. That write-eligibility
# policy itself governs a skill that writes to these fields; this pipeline
# never writes to Baserow at all, so the policy's write rules are Not
# Applicable here. What DOES carry over is the underlying reasoning for why
# these fields are unreliable-until-reviewed data, which is exactly why this
# pipeline continues to exclude all seven from both Kumu exports on the read
# side. They split into two categories with different reasons for exclusion,
# not one blanket reason:
#
#   Category A -- staging inputs, inherently unreviewed:
#     orgs-user-nominated, communities-lead-user-nominated,
#     communities-participant-user-nominated, notes-user-nominated
#   These hold exactly what a person typed on the self-nomination form.
#   They are NOT meant to be read by anything other than Cass's own manual
#   review process, which decides whether/how to promote each one into its
#   real structured field (organisations / communities-lead /
#   communities-participant / notes). Permanently excluded from Kumu on
#   this basis -- there is no "finished" state for Kumu to read from these
#   fields even in principle; the finished state is the real field they get
#   promoted into, which this pipeline already reads normally.
#
#   Category B -- real facts, but always flagged for human review:
#     pronouns-user-nominated, git-other-user-nominated,
#     socials-other-user-nominated
#   Unlike Category A, these ARE the field of record for a genuine fact
#   that doesn't fit the picklist/format of the real field (e.g. pronouns
#   outside the fixed options). But any skill writing to them is required
#   to mark the write for human review, never silently accept it as
#   settled -- and Baserow currently has no "reviewed" status field for
#   these three that this pipeline could check. So excluded from Kumu for
#   now not because the data is inherently unusable (unlike Category A),
#   but because there is currently no signal available to this pipeline
#   distinguishing a reviewed value from a fresh, unreviewed one.
#
# FUTURE DEVELOPMENT (not yet built): if a "reviewed" status field is ever
# added to Baserow for the Category B three (e.g. a checkbox per field, or
# one shared review-status field), this pipeline could safely include them
# -- gated on that flag being true -- in both exports, subject to the same
# consent tier as the rest of a person's profile. Until that field exists,
# leave all seven excluded.
# ---------------------------------------------------------------------------

PROFILE_FIELDS = {
    "Person": [
        "carrer-current-role-title", "pronouns", "career-stage", "notes",
        "email-1", "email-2", "email-3", "github", "institutional-profile",
        "linkedin", "ORCID",
        # confirmed 2026-09-10: this is a MULTISELECT (options: communications,
        # engagement, project management, strategic, technical) describing the
        # *kind* of contribution a person makes, not a link to a specific
        # Community row -- so it's a profile attribute, not an edge. Carried
        # through as-is (pipe-joined like the other multi-value columns) via
        # split_multi/join_pipe in pipeline.py, same as any other field here.
        # PARKED per Cass: come back to whether this should also feed into
        # edge typing (e.g. contributor-technical vs contributor-strategic)
        # once the generic-vs-scoped edge-type question is revisited.
        "communities-contributor-profile",
    ],
    "Organisation": ["type", "notes", "website"],
    "Community": ["description", "website"],
    "Project": ["description", "status", "date-start", "date-end", "website"],
}

# Profile fields that are actually multi-value (multiselect / link fields
# carried as metadata rather than as an edge) and so need the same
# comma-to-pipe treatment as edge/interaction-rollup fields. Plain free-text
# fields (notes, etc.) are deliberately NOT in here -- splitting those on
# commas would corrupt ordinary sentences.
MULTISELECT_PROFILE_FIELDS = {
    "Person": ["communities-contributor-profile", "pronouns"],
}

# ---------------------------------------------------------------------------
# Fields on Person profiles blanked out for a PSEUDONYMISED public export
# (consent-public-pseudonymised) -- i.e. the person still appears on the
# public map under a stable hashed label, but these fields are stripped.
# Excluded (no-consent) people don't reach this list at all -- they're
# dropped from the public export entirely, element and edges both.
#
# Current split, confirmed by Cass (2026-09-24):
#   excluded: email-1, github, institutional-profile, linkedin, ORCID,
#             pronouns, carrer-current-role-title
#   included: career-stage, communities-contributor-profile
# ("notes", "email-2", "email-3" used to be here too; they're now handled
# separately below, as internal-only regardless of consent tier -- see
# PERSON_INTERNAL_ONLY_FIELDS.)
#
# Not yet addressed (flagged, not decided): relationship/edge fields
# (organisations, communities-lead, communities-participant, projects-*,
# interactions-lead/-participant) are NOT filtered by consent at all right
# now -- a pseudonymised person's connections to Orgs/Communities/Projects
# still show up on the map under their pseudonym. Whether that should also
# be restricted is a separate question from field-blanking and hasn't been
# decided either way yet.
# ---------------------------------------------------------------------------

PERSON_IDENTIFIABLE_FIELDS = [
    "email-1", "github", "institutional-profile",
    "linkedin", "ORCID", "pronouns", "carrer-current-role-title",
]

# ---------------------------------------------------------------------------
# Fields kept ONLY on the internal export, stripped from the public export
# for EVERY Person regardless of consent tier -- including
# consent-public-identifiable, which is otherwise untouched by the
# pseudonymised-only blanking list above.
#
# "notes" -- confirmed by Cass (2026-09-24): always internal-only, since
# free-text notes can carry identifying or sensitive detail that a person's
# consent to appear on the public map (even under their real name) doesn't
# cover -- consenting to be shown isn't the same as consenting to have
# arbitrary staff-written notes about you made public.
#
# "email-2" / "email-3" -- confirmed by Cass (2026-09-24): these are likely
# to be personal (not professional) addresses kept as backups, not the
# address a person would choose to have published even under public
# identifiable consent. Convention going forward (to be documented in the
# maintenance notes): email-1 is reviewed/maintained as the person's primary
# PROFESSIONAL email specifically because it's the only one ever shown
# publicly -- email-2/3 don't need that same scrutiny since they never
# leave the internal export.
#
# FUTURE DEVELOPMENT (not yet built): two new People fields are planned --
# mission-interest and mission-influence (naming TBC) -- for mapping a
# person's interest in / influence over RCM Cooperative's mission. These
# do not exist in the current Baserow schema yet. When added: (1) add them
# to config.EXPECTED_COLUMNS["People"], (2) add them to
# PROFILE_FIELDS["Person"] so they're read into the export at all, and
# (3) add them here, to PERSON_INTERNAL_ONLY_FIELDS -- confirmed by Cass
# (2026-09-24) that these must NEVER be published, at any consent tier.
# ---------------------------------------------------------------------------

PERSON_INTERNAL_ONLY_FIELDS = ["notes", "email-2", "email-3"]



# ---------------------------------------------------------------------------
# Consent tiers (Baserow single-select options on People.mapping-consent)
# and how each behaves in the two Kumu exports this pipeline produces.
#
#   internal export -> for RCM Cooperative's own internal use. Every person
#                       appears with their real name and full profile,
#                       regardless of consent tier (consent-internal exists
#                       precisely to permit this).
#   public export   -> for the public-facing Kumu map. Only people who have
#                       actively given PUBLIC consent appear at all.
#
# Confirmed by Cass (2026-09-24): people at consent-not-asked / consent-none
# / consent-internal are EXCLUDED entirely from the public export (not
# merely pseudonymised) -- a deliberate departure from the old SharePoint-
# era script, which anonymised but still showed everyone.
# ---------------------------------------------------------------------------

CONSENT_PUBLIC_IDENTIFIABLE = "consent-public-identifiable"
CONSENT_PUBLIC_PSEUDONYMISED = "consent-public-pseudonymised"
CONSENT_INTERNAL_ONLY = {"consent-internal", "consent-none", "consent-not-asked"}

PUBLIC_CONSENT_TIERS = {CONSENT_PUBLIC_IDENTIFIABLE, CONSENT_PUBLIC_PSEUDONYMISED}

# Non-Person node types have no consent field at all -- always public,
# matching the old script's "if type != Person, consent = public" default.

# ---------------------------------------------------------------------------
# type-display granularity: for most node types the display legend just
# shows the node type itself (Person / Organisation / Community / Project).
# Some tables have a more granular field worth showing instead -- e.g.
# Organisations.type distinguishes academic institutes from non-profits.
# Maps node type -> source field name; falls back to the plain type name
# if the row's value in that field is blank.
# ---------------------------------------------------------------------------

TYPE_DISPLAY_SOURCE_FIELD = {
    "Organisation": "type",
}
