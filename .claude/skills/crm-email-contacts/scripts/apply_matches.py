"""
apply_matches.py

Takes the candidate-match spreadsheet after a human has reviewed it
(filled 'confirm' with "yes" on rows they accept, optionally editing the
email-1, email-2, ... columns) and writes those emails into a copy of the
original Baserow People export.

A matched contact can have more than one email address (e.g. work +
personal); match_candidates.py lays these out as separate email-1,
email-2, email-3, ... columns rather than one combined field, matching
the Baserow People table's own naming convention. This script writes
each of those columns straight into the corresponding email-N column on
the People export, creating the column if the People export doesn't
already have it.

A confirmed row with `in_crm=0` (a contact match_candidates.py couldn't
match to anyone already in the People export) is appended as a brand-new
row instead of updating an existing one — name and email(s) filled in,
everything else blank.

Nothing is written to Baserow directly — per the current workflow,
the output file is meant to be manually copy-pasted into the live
Baserow table.

The output file also includes an "Organisations" tab, populated with the
distinct org_domain values found among this run's confirmed matches (one
row per organisation, in name-org-long) — not just an empty schema
template. It's a starting-point candidate list for organisations that
came up in this batch, meant for review/completion before copy-pasting
into the live Organisations table; nothing here is written to Baserow
automatically, and duplicates against existing Organisations rows are
not checked.

Column order is NOT matched to Baserow's on-screen order. This was tried
(a hardcoded, screenshot-derived order list) and dropped: the field-
definitions API's own "order" property doesn't reflect true on-screen
position, so keeping it accurate meant re-screenshotting the live table
periodically — which already needed correcting once as the schema grew
(new fields, including a public self-nomination form's worth of columns,
kept appearing outside the hardcoded list). Baserow's import feature can
match by column header name rather than position, which would remove the
need for this entirely — deliberately out of scope for now, scoped as
further development. Consequences of dropping ordering, practical and
otherwise: the People sheet keeps whatever column order the input
`--people` export already had, with any new columns appended at the end;
the Organisations sheet uses a plain, arbitrary column order of this
skill's own choosing (not derived from Baserow at all). **This means the
output will very likely need a manual column reorder in Excel before
pasting into live Baserow** — this pipeline no longer does that
alignment for you. The upside: no more hardcoded, easily-stale order
list to maintain, and no risk of the pipeline enforcing a wrong or
outdated order onto a Baserow base your own instance may have organised
differently (relevant if this base is templated by someone else).

Usage:
    # Using the dated-folder convention (fills in --candidates/--output defaults):
    python apply_matches.py \
        --date 20260905 \
        --people baserow-export-people-20260907.xlsx \
        --people-name-column "name-person" \
        --people-email-column "email-1"

    # Or with explicit paths:
    python apply_matches.py \
        --people baserow-export-people-20260907.xlsx \
        --candidates candidate_matches_reviewed.xlsx \
        --people-name-column "name-person" \
        --people-email-column "email-1" \
        --output people_export_updated.xlsx

Requires:
    pip install pandas openpyxl --break-system-packages
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

DEFAULT_BASE_DIR = "private/email-contacts"
EMAIL_COLUMN_PATTERN = re.compile(r"^email-(\d+)$")

# Plain, arbitrary column order for the Organisations sheet this script
# builds from scratch — NOT claimed to match Baserow's on-screen order
# (that guarantee was dropped; see the module docstring above for why).
# Just a sensible reading order: names first, then descriptive fields,
# then relationship links.
ORGANISATIONS_SHEET_COLUMN_ORDER = [
    "name-org-long", "name-org-abbreviation", "type", "website", "notes",
    "people-employees", "communities-sponsor", "projects-sponsor",
    "projects-funder", "interactions-sponsor", "interactions-funder",
]


def find_email_columns(df):
    """Return email-N column names present in df, sorted numerically (email-1, email-2, ...)."""
    matches = [(int(m.group(1)), col) for col in df.columns for m in [EMAIL_COLUMN_PATTERN.match(col)] if m]
    matches.sort(key=lambda pair: pair[0])
    return [col for _, col in matches]


def main():
    parser = argparse.ArgumentParser(
        description="Apply human-confirmed email matches into a copy of the People export."
    )
    parser.add_argument("--people", required=True, help="Original Baserow People export (.csv or .xlsx)")
    parser.add_argument("--candidates", help="Reviewed candidate-match spreadsheet (default: candidate_matches_<date>.xlsx in the dated folder, if --date is given)")
    parser.add_argument("--date", help="Export date as it appears in the folder name, e.g. 20260905 (used to derive --candidates/--output defaults)")
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR, help=f"Base folder the dated export folders live under (default: {DEFAULT_BASE_DIR})")
    parser.add_argument("--people-name-column", required=True, help="Column in the People export holding the person's full name")
    parser.add_argument("--people-email-column", default="email-1", help="Accepted for CLI symmetry with the other stages; not used by this script — every email-N column found in the candidates file is written regardless")
    parser.add_argument("--output", help="Where to write the updated People spreadsheet (default: people_export_updated_<date>.xlsx in the dated folder, if --date is given)")
    args = parser.parse_args()

    candidates_path = args.candidates
    output_path = args.output

    if not candidates_path:
        if not args.date:
            print("No --candidates given and no --date to derive it from — please pass one of the two.", file=sys.stderr)
            sys.exit(1)
        candidates_path = str(Path(args.base_dir) / f"all-contacts-{args.date}" / f"candidate_matches_{args.date}.xlsx")

    if not output_path:
        if args.date:
            output_path = str(Path(args.base_dir) / f"all-contacts-{args.date}" / f"people_export_updated_{args.date}.xlsx")
        else:
            # No --date given — default to writing alongside --people, since
            # the output is an updated copy of that file's data.
            output_path = str(Path(args.people).parent / "people_export_updated.xlsx")

    if args.people.lower().endswith(".xlsx"):
        people_df = pd.read_excel(args.people)
    else:
        people_df = pd.read_csv(args.people)

    candidates_df = pd.read_excel(candidates_path)

    if args.people_name_column not in people_df.columns:
        raise SystemExit(
            f"Column '{args.people_name_column}' not found in {args.people}. "
            f"Available columns: {list(people_df.columns)}"
        )

    email_cols = find_email_columns(candidates_df)
    if not email_cols:
        raise SystemExit(
            f"No email-N columns (email-1, email-2, ...) found in {candidates_path}. "
            f"Available columns: {list(candidates_df.columns)}"
        )

    # Make sure every email-N column exists on the People side too, and force
    # a text-friendly dtype up front: if every row in a column is blank,
    # pandas/openpyxl reads it back as an all-NaN float64 column, which then
    # rejects string assignment below.
    for col in email_cols:
        if col not in people_df.columns:
            people_df[col] = ""
        people_df[col] = people_df[col].astype(object)

    confirmed = candidates_df[
        candidates_df["confirm"].astype(str).str.strip().str.lower().isin(["yes", "y"])
    ]

    if confirmed.empty:
        print("No rows marked 'yes' in the confirm column. Nothing to apply.")
        return

    rows_applied = 0
    emails_written = 0
    skipped_no_email = 0
    skipped_no_match_in_people = 0
    new_people_added = 0
    appended_rows = []
    org_domains_found = []  # preserves first-seen order; deduped case-insensitively below

    for _, cand in confirmed.iterrows():
        baserow_name = cand.get("baserow_name", "")

        org_domain_value = str(cand.get("matched_contact_org_domain", "")).strip()
        if org_domain_value and org_domain_value.lower() != "nan":
            org_domains_found.append(org_domain_value)

        row_emails = []
        for col in email_cols:
            value = str(cand.get(col, "")).strip()
            if value and value.lower() != "nan":
                row_emails.append((col, value))

        in_crm_value = str(cand.get("in_crm", "1")).strip()
        is_new_person = in_crm_value in ("0", "0.0")

        if is_new_person:
            # Not an existing Baserow person at all (in_crm=0) — append as a
            # brand-new row rather than trying to match/update one that
            # doesn't exist. Name comes from the contact, since baserow_name
            # is blank for these rows.
            new_row = {col: "" for col in people_df.columns}
            new_row[args.people_name_column] = cand.get("matched_contact_name", "")
            for col, value in row_emails:
                new_row[col] = value
            appended_rows.append(new_row)
            new_people_added += 1
            continue

        if not row_emails:
            skipped_no_email += 1
            continue

        match_mask = people_df[args.people_name_column] == baserow_name
        if not match_mask.any():
            skipped_no_match_in_people += 1
            continue

        # Write only into currently-blank email-N slots — never overwrite an
        # email that's already there. This matters now that a candidate row
        # can represent someone who already has an email (they were matched
        # here for a missing organisation instead) — confirming that row
        # must not clobber their existing address.
        any_written = False
        for idx in people_df.index[match_mask]:
            for col, value in row_emails:
                current = str(people_df.at[idx, col]).strip()
                if not current or current.lower() == "nan":
                    people_df.at[idx, col] = value
                    emails_written += 1
                    any_written = True

        if any_written:
            rows_applied += 1

    if appended_rows:
        people_df = pd.concat([people_df, pd.DataFrame(appended_rows)], ignore_index=True)

    # Dedupe organisations case-insensitively, keeping the first-seen casing
    seen_lower = set()
    unique_orgs = []
    for org in org_domains_found:
        key = org.lower()
        if key not in seen_lower:
            seen_lower.add(key)
            unique_orgs.append(org)

    # Build the Organisations sheet with a plain, useful set of columns
    # (blank), then populate name-org-long with the organisations found.
    # Not attempting full real-schema completeness here (formula/system
    # fields dropped) since this is a candidate list for review, not a
    # copy-paste-range-matching export.
    organisations_df = pd.DataFrame({col: [""] * len(unique_orgs) for col in ORGANISATIONS_SHEET_COLUMN_ORDER})
    organisations_df["name-org-long"] = unique_orgs

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        people_df.to_excel(writer, sheet_name="People", index=False)
        organisations_df.to_excel(writer, sheet_name="Organisations", index=False)

    print(f"Confirmed rows in candidate file: {len(confirmed)}")
    print(f"Existing People rows updated: {rows_applied}")
    print(f"New People rows added (in_crm=0, confirmed): {new_people_added}")
    print(f"Total email values written across {', '.join(email_cols)}: {emails_written}")
    if skipped_no_email:
        print(f"Skipped (no email-N value filled in): {skipped_no_email}")
    if skipped_no_match_in_people:
        print(f"Skipped (name no longer found in People export — was it edited?): {skipped_no_match_in_people}")
    print(f"Organisations found from confirmed matches: {len(unique_orgs)}")
    print(f"Output: {output_path} (sheets: People, Organisations)")
    print()
    print("WARNING: column order in this output is NOT matched to Baserow's live "
          "on-screen order — that guarantee was dropped (see the top of this script "
          "for why). Before pasting into Baserow, open this file in Excel and manually "
          "check/reorder each sheet's columns against a current screenshot of the live "
          "table first — pasting misaligned columns will write data into the wrong fields.")
    print()
    print("Next step: open this file, copy each sheet's populated range (after "
          "reordering columns as above), and paste into the corresponding live "
          "Baserow table.")


if __name__ == "__main__":
    main()
