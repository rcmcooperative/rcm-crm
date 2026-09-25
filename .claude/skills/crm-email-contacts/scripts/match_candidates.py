"""
match_candidates.py

Fuzzy-matches parsed Google Contacts (name, email) rows against an exported
Baserow "People" table, and produces a ranked candidate-match spreadsheet
for a human to review and confirm — no data is written back to Baserow
by this script, and no LLM is used anywhere in the matching itself.

Matching is pure string comparison (Python's stdlib difflib), using a
normalised (lower-cased, punctuation-stripped, token-order-invariant)
form of each name so that e.g. "Smith, Bob" and "Bob Smith" still match.

A Baserow person is considered for matching if they're missing EITHER
their email OR their organisation link (--people-org-column, e.g. the
"organisations" link field) — not only when the email is blank. This
means someone who already has an email can still appear here (to surface
their org_domain), and someone who already has an organisation can still
appear here (to surface an email) — the two are filled independently at
apply time, never overwriting whichever of the two is already present.
`already_has_email` / `already_has_org` columns in the output make clear
which is actually needed for each row.

An `org_domain` column is carried through from `parsed_contacts.csv` into
the review spreadsheet as `matched_contact_org_domain` — the email
domain's organisation label, e.g. "UCL" (see parse_vcf.py for how this is
derived and capitalised). It's not matched or validated against Baserow's
Organisations table — it's shown purely as reference for the human
reviewer.

Every contact in `parsed_contacts.csv` is represented in the output, not
just ones matched to an existing Baserow person — a contact with no
match at all still gets a row, with `in_crm` set to `0` and
`baserow_name` left blank, so confirming it (typing `yes`) tells
apply_matches.py to add them as a brand-new People row rather than
update an existing one. `in_crm` is `1` for a genuine name match against
an existing Baserow person, `0` for a contact apply_matches.py hasn't
seen anywhere in the People export.

When a matched contact has more than one email address, they're written
out as separate email-1, email-2, email-3, ... columns (matching the
Baserow People table's own naming convention), not crammed into one
column — so a confirmed row can be applied straight across without any
reshaping.

Usage:
    # Using the dated-folder convention (fills in --contacts/--output defaults):
    python match_candidates.py \
        --date 20260905 \
        --people baserow-export-people-20260907.xlsx \
        --people-name-column "name-person" \
        --people-email-column "email-1" \
        --people-org-column "organisations"

    # Or with explicit paths:
    python match_candidates.py \
        --contacts parsed_contacts.csv \
        --people baserow-export-people-20260907.xlsx \
        --people-name-column "name-person" \
        --people-email-column "email-1" \
        --people-org-column "organisations" \
        --output candidate_matches.xlsx \
        --min-score 60

Requires:
    pip install pandas openpyxl --break-system-packages
"""

import argparse
import difflib
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

DEFAULT_BASE_DIR = "private/email-contacts"


def normalise(name):
    """Lower-case, strip punctuation, collapse whitespace, sort tokens."""
    if not isinstance(name, str):
        return ""
    cleaned = re.sub(r"[^\w\s]", " ", name.lower())
    tokens = sorted(cleaned.split())
    return " ".join(tokens)


def similarity(a, b):
    """Return a 0-100 similarity score between two normalised name strings."""
    if not a or not b:
        return 0.0
    return round(difflib.SequenceMatcher(None, a, b).ratio() * 100, 1)


def build_contact_index(contacts_df):
    """Group parsed contact rows by normalised name -> list of (raw_name, email, org_domain)."""
    index = defaultdict(list)
    for _, row in contacts_df.iterrows():
        norm = normalise(row.get("name", ""))
        if not norm:
            continue
        index[norm].append(
            {
                "raw_name": row.get("name", ""),
                "email": row.get("email", "") or "",
                "org_domain": row.get("org_domain", "") or "",
            }
        )
    return index


def find_best_matches(person_name, contact_index):
    """
    Compare one Baserow person's normalised name against every distinct
    normalised contact name. Returns (best, runner_up) score/name tuples.
    """
    norm_person = normalise(person_name)
    scored = []
    for norm_contact, entries in contact_index.items():
        score = similarity(norm_person, norm_contact)
        if score > 0:
            scored.append((score, norm_contact, entries))
    scored.sort(key=lambda x: x[0], reverse=True)

    best = scored[0] if len(scored) >= 1 else None
    runner_up = scored[1] if len(scored) >= 2 else None
    return best, runner_up


def main():
    parser = argparse.ArgumentParser(
        description="Fuzzy-match parsed Google Contacts against a Baserow People export."
    )
    parser.add_argument("--contacts", help="parsed_contacts.csv from parse_vcf.py (default: parsed_contacts_<date>.csv in the dated folder, if --date is given)")
    parser.add_argument("--date", help="Export date as it appears in the folder name, e.g. 20260905 (used to derive --contacts/--output defaults)")
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR, help=f"Base folder the dated export folders live under (default: {DEFAULT_BASE_DIR})")
    parser.add_argument("--people", required=True, help="Baserow People export (.csv or .xlsx)")
    parser.add_argument("--people-name-column", required=True, help="Column in the People export holding the person's full name")
    parser.add_argument("--people-email-column", default="email-1", help="Column in the People export holding their existing email (default: email-1)")
    parser.add_argument("--people-org-column", default="organisations", help="Column in the People export holding their linked organisation(s) (default: organisations)")
    parser.add_argument("--people-id-column", default=None, help="Optional column with a stable row ID, kept in the output for traceability")
    parser.add_argument("--output", help="Where to write the candidate-match spreadsheet (default: candidate_matches_<date>.xlsx in the dated folder, if --date is given)")
    parser.add_argument("--min-score", type=float, default=60.0, help="Only include candidates scoring at or above this (0-100). Default: 60")
    args = parser.parse_args()

    contacts_path = args.contacts
    output_path = args.output

    if not contacts_path:
        if not args.date:
            print("No --contacts given and no --date to derive it from — please pass one of the two.", file=sys.stderr)
            sys.exit(1)
        contacts_path = str(Path(args.base_dir) / f"all-contacts-{args.date}" / f"parsed_contacts_{args.date}.csv")

    if not output_path:
        if args.date:
            output_path = str(Path(args.base_dir) / f"all-contacts-{args.date}" / f"candidate_matches_{args.date}.xlsx")
        else:
            # No --date given — default to writing alongside --contacts, so
            # output lands in the same directory the input data came from.
            output_path = str(Path(contacts_path).parent / "candidate_matches.xlsx")

    contacts_df = pd.read_csv(contacts_path)

    if args.people.lower().endswith(".xlsx"):
        people_df = pd.read_excel(args.people)
    else:
        people_df = pd.read_csv(args.people)

    if args.people_name_column not in people_df.columns:
        raise SystemExit(
            f"Column '{args.people_name_column}' not found in {args.people}. "
            f"Available columns: {list(people_df.columns)}"
        )

    contact_index = build_contact_index(contacts_df)

    has_org_column = args.people_org_column in people_df.columns
    if not has_org_column:
        print(
            f"Note: column '{args.people_org_column}' not found in {args.people} — "
            "can't check for a missing organisation, so only matching people missing an email "
            "(pass --people-org-column if it's named differently).",
            file=sys.stderr,
        )

    rows_out = []
    skipped_fully_covered = 0
    max_email_count = 1  # always emit at least one email-N column, even if empty
    matched_contact_norms = set()  # normalised contact names matched to any Baserow person

    for _, person in people_df.iterrows():
        existing_email = person.get(args.people_email_column, "")
        already_has_email = isinstance(existing_email, str) and bool(existing_email.strip())

        if has_org_column:
            existing_org = person.get(args.people_org_column, "")
            already_has_org = isinstance(existing_org, str) and bool(existing_org.strip())
        else:
            # Can't check — fall back to the original email-only behaviour
            # rather than matching everyone.
            already_has_org = True

        person_name = person.get(args.people_name_column, "")
        if not isinstance(person_name, str) or not person_name.strip():
            continue

        best, runner_up = find_best_matches(person_name, contact_index)
        if best is None or best[0] < args.min_score:
            if already_has_email and already_has_org:
                skipped_fully_covered += 1
            continue

        best_score, matched_norm, best_entries = best
        matched_contact_norms.add(matched_norm)

        if already_has_email and already_has_org:
            skipped_fully_covered += 1
            continue  # matched, but nothing missing for this existing person

        runner_up_score = runner_up[0] if runner_up else ""

        # A name can have more than one email on the Google Contacts side
        # (e.g. work + personal) — dedupe while keeping order, since the
        # same address can legitimately appear twice across vCard fields.
        seen = set()
        candidate_emails = []
        for e in best_entries:
            if e["email"] and e["email"] not in seen:
                seen.add(e["email"])
                candidate_emails.append(e["email"])

        max_email_count = max(max_email_count, len(candidate_emails))

        row = {
            "baserow_name": person_name,
            "in_crm": 1,
            "matched_contact_name": best_entries[0]["raw_name"],
            "matched_contact_org_domain": best_entries[0]["org_domain"],
            "match_score": best_score,
            "runner_up_score": runner_up_score,
            "already_has_email": "yes" if already_has_email else "no",
            "already_has_org": "yes" if already_has_org else "no",
            "_candidate_emails": candidate_emails,  # expanded into email-N columns below
            "confirm": "",  # human fills in "yes" to accept — left blank deliberately
        }
        if args.people_id_column and args.people_id_column in people_df.columns:
            row["baserow_row_id"] = person.get(args.people_id_column, "")

        rows_out.append(row)

    # Contacts that never matched any Baserow person at all — not in the CRM
    # yet. Still surfaced, with in_crm=0 and no baserow_name, so confirming
    # one tells apply_matches.py to add them as a new row rather than update
    # an existing one.
    new_contact_rows = 0
    for norm, entries in contact_index.items():
        if norm in matched_contact_norms:
            continue

        seen = set()
        candidate_emails = []
        for e in entries:
            if e["email"] and e["email"] not in seen:
                seen.add(e["email"])
                candidate_emails.append(e["email"])

        max_email_count = max(max_email_count, len(candidate_emails))
        org_domain = next((e["org_domain"] for e in entries if e["org_domain"]), "")

        row = {
            "baserow_name": "",
            "in_crm": 0,
            "matched_contact_name": entries[0]["raw_name"],
            "matched_contact_org_domain": org_domain,
            "match_score": None,
            "runner_up_score": None,
            "already_has_email": "",
            "already_has_org": "",
            "_candidate_emails": candidate_emails,
            "confirm": "",
        }
        rows_out.append(row)
        new_contact_rows += 1

    if not rows_out:
        print("No candidate matches found above the score threshold. Nothing written.")
        return

    # Expand each row's candidate email list into email-1, email-2, ... columns
    # — matching the Baserow People table's own email-1/email-2/email-3 naming,
    # so the reviewed spreadsheet can be applied straight across without any
    # reshaping. Rows with fewer emails than the row-wide max are left blank
    # in the higher-numbered columns.
    email_col_names = [f"email-{i}" for i in range(1, max_email_count + 1)]
    for row in rows_out:
        candidate_emails = row.pop("_candidate_emails")
        for i, col_name in enumerate(email_col_names):
            row[col_name] = candidate_emails[i] if i < len(candidate_emails) else ""

    out_df = pd.DataFrame(rows_out).sort_values("match_score", ascending=False, na_position="last")

    # Column order: identifying/scoring columns, then email-1..email-N, then confirm last
    ordered_cols = ["baserow_name", "in_crm", "matched_contact_name", "matched_contact_org_domain", "match_score", "runner_up_score", "already_has_email", "already_has_org"]
    ordered_cols += email_col_names
    ordered_cols += ["confirm"]
    if "baserow_row_id" in out_df.columns:
        ordered_cols.insert(0, "baserow_row_id")
    out_df = out_df[ordered_cols]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_excel(output_path, index=False)

    print(f"Baserow People rows already fully covered (have both email and org — skipped): {skipped_fully_covered}")
    print(f"Candidate matches against existing Baserow people (in_crm=1): {len(out_df) - new_contact_rows}")
    print(f"Contacts not found anywhere in Baserow at all (in_crm=0, new people): {new_contact_rows}")
    print(f"Email columns in output: {', '.join(email_col_names)}")
    print(f"Output: {output_path}")
    print()
    print("Next step: open this file, review each row, and type 'yes' in the "
          "'confirm' column for matches you accept (edit the email-N columns "
          "first if a value is wrong or you want to drop one). Check "
          "'already_has_email'/'already_has_org' to see what's actually being "
          "proposed for each row — confirming won't overwrite whichever one "
          "the person already has. For in_crm=0 rows, confirming adds them as "
          "a brand-new person rather than updating an existing one. Then run "
          "apply_matches.py.")


if __name__ == "__main__":
    main()
