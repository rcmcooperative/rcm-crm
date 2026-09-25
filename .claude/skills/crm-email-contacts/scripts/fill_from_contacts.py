"""
fill_from_contacts.py

A more automated alternative to the match_candidates.py / apply_matches.py
review flow: matches parsed Google Contacts against a Baserow People
export by EXACT normalised name (not fuzzy-scored), and writes matched
emails and an org_domain value directly into a copy of the People export
— no separate human-confirmation spreadsheet step in between.

Because there's no confirm-column checkpoint here, matching is
deliberately stricter than match_candidates.py: a name must match
exactly (after lower-casing, punctuation-stripping, and word-order
normalisation) rather than merely score highly on similarity. Anything
that can't be resolved with confidence is flagged in yellow rather than
guessed at:

  - A Baserow person whose normalised name matches MORE THAN ONE other
    Baserow person (a duplicate/near-duplicate name within the People
    export itself) is left untouched and its row highlighted yellow —
    there's no reliable way to know which one a contact's email belongs
    to, so nothing is written for any of them.
  - A contact name that doesn't match anyone in the People export is
    appended as a brand new row at the end (filled in as best it can:
    name, email(s), org_domain — everything else left blank), and that
    row is highlighted yellow, since it's new and unverified.
  - Any newly created column (a new email-N slot, or the org_domain
    column if the People export didn't already have one) is highlighted
    yellow across its header and every cell, so it's obvious at a glance
    what this run added to the table structure.

Email-filling behaviour matches apply_matches.py: existing blank email-N
slots are filled first, in order; a new email-(N+1) column is only
created once every existing slot is full for at least one row; an email
already present anywhere in that row's email-N columns is never added
again. org_domain is only filled in where currently blank — an existing
value is never overwritten.

No LLM involvement anywhere in this script.

Usage:
    # Parse a .vcf and fill in one step, using the dated-folder convention:
    python fill_from_contacts.py \
        --date 20260907 \
        --people baserow-export-people-20260907.xlsx \
        --people-name-column "name-person"

    # Or reuse an already-parsed contacts CSV:
    python fill_from_contacts.py \
        --contacts parsed_contacts_20260907.csv \
        --people baserow-export-people-20260907.xlsx \
        --people-name-column "name-person" \
        --output baserow-export-people-20260907-emails-added.xlsx

Requires:
    pip install vobject tldextract pandas openpyxl --break-system-packages
"""

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from openpyxl.styles import PatternFill

from match_candidates import normalise
from parse_vcf import DEFAULT_BASE_DIR, parse_vcf, prompt_for_date, resolve_vcf_path

EMAIL_COLUMN_PATTERN = re.compile(r"^email-(\d+)$")
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


def find_email_columns(columns):
    """Return email-N column names present, sorted numerically (email-1, email-2, ...)."""
    matches = [(int(m.group(1)), col) for col in columns for m in [EMAIL_COLUMN_PATTERN.match(col)] if m]
    matches.sort(key=lambda pair: pair[0])
    return [col for _, col in matches]


def build_contact_groups(contacts_df):
    """Group contact rows by normalised name -> deduped emails + first org_domain found."""
    raw_groups = defaultdict(list)
    for _, row in contacts_df.iterrows():
        norm = normalise(row.get("name", ""))
        if not norm:
            continue
        raw_groups[norm].append(
            {
                "raw_name": row.get("name", ""),
                "email": row.get("email", "") or "",
                "org_domain": row.get("org_domain", "") or "",
            }
        )

    groups = {}
    for norm, entries in raw_groups.items():
        seen_emails = set()
        emails = []
        for e in entries:
            if e["email"] and e["email"] not in seen_emails:
                seen_emails.add(e["email"])
                emails.append(e["email"])
        org_domain = next((e["org_domain"] for e in entries if e["org_domain"]), "")
        groups[norm] = {
            "raw_name": entries[0]["raw_name"],
            "emails": emails,
            "org_domain": org_domain,
        }
    return groups


def main():
    parser = argparse.ArgumentParser(
        description="Match parsed Google Contacts against a Baserow People export by exact "
        "normalised name, and write emails/org_domain directly (no review-spreadsheet step)."
    )
    parser.add_argument("--input", help="Path to a specific .vcf file (parsed fresh, bypassing the dated-folder convention)")
    parser.add_argument("--date", help="Export date as it appears in the folder name, e.g. 20260907 (used to locate/parse the .vcf, or to default --contacts if no .vcf is found)")
    parser.add_argument("--contacts", help="An already-parsed contacts CSV (from parse_vcf.py) — skips re-parsing a .vcf")
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR, help=f"Base folder the dated export folders live under (default: {DEFAULT_BASE_DIR})")
    parser.add_argument("--people", required=True, help="Baserow People export (.csv or .xlsx)")
    parser.add_argument("--people-name-column", required=True, help="Column in the People export holding the person's full name")
    parser.add_argument("--output", help="Where to write the updated People spreadsheet (default: alongside --people, or in the dated folder if --date is given)")
    args = parser.parse_args()

    # --- Resolve contacts data: explicit CSV > explicit .vcf > date-resolved .vcf ---
    contacts_df = None
    if args.contacts:
        contacts_df = pd.read_csv(args.contacts)
    else:
        vcf_path = args.input
        if not vcf_path:
            date_str = args.date or prompt_for_date()
            matches, dirs_tried = resolve_vcf_path(date_str, args.base_dir)
            if not matches:
                print(
                    f"No .vcf file found for date '{date_str}'. Looked in:\n  "
                    + "\n  ".join(dirs_tried)
                    + "\nPass --input or --contacts directly, or check the folder/date.",
                    file=sys.stderr,
                )
                sys.exit(1)
            if len(matches) > 1:
                print(
                    f"Found more than one .vcf file for date '{date_str}':\n  "
                    + "\n  ".join(matches)
                    + "\nPass --input to pick one directly.",
                    file=sys.stderr,
                )
                sys.exit(1)
            vcf_path = matches[0]
            print(f"Resolved .vcf from date '{date_str}': {vcf_path}")

        records, _ = parse_vcf(vcf_path)
        contacts_df = pd.DataFrame(records)

    if contacts_df is None or contacts_df.empty:
        print("No contact records available. Nothing to do.", file=sys.stderr)
        sys.exit(1)

    # --- Resolve output path ---
    output_path = args.output
    if not output_path:
        if args.date:
            output_path = str(Path(args.base_dir) / f"all-contacts-{args.date}" / f"people_export_filled_{args.date}.xlsx")
        else:
            output_path = str(Path(args.people).parent / "people_export_filled.xlsx")

    # --- Load People export ---
    if args.people.lower().endswith(".xlsx"):
        people_df = pd.read_excel(args.people)
    else:
        people_df = pd.read_csv(args.people)

    if args.people_name_column not in people_df.columns:
        raise SystemExit(
            f"Column '{args.people_name_column}' not found in {args.people}. "
            f"Available columns: {list(people_df.columns)}"
        )

    # --- Detect ambiguous (duplicate-normalised-name) People rows: flag, don't fill ---
    people_norm_names = people_df[args.people_name_column].apply(normalise)
    name_counts = Counter(n for n in people_norm_names if n)
    ambiguous_norms = {n for n, count in name_counts.items() if count > 1}
    ambiguous_row_indices = [i for i, n in enumerate(people_norm_names) if n in ambiguous_norms]

    # --- Build contact groups, excluding any whose name is ambiguous on the Baserow side ---
    contact_groups = build_contact_groups(contacts_df)

    # --- Ensure email-N and org_domain columns exist with a text-friendly dtype ---
    existing_email_cols = find_email_columns(people_df.columns)
    if not existing_email_cols:
        existing_email_cols = ["email-1"]
        people_df["email-1"] = ""
    for col in existing_email_cols:
        people_df[col] = people_df[col].astype(object)

    org_domain_is_new = "org_domain" not in people_df.columns
    if org_domain_is_new:
        people_df["org_domain"] = ""
    people_df["org_domain"] = people_df["org_domain"].astype(object)

    # --- Pass 1: work out how many extra email columns the busiest matched row needs ---
    extra_columns_needed = 0
    matched_plan = {}  # row index -> list of new emails to add (in order)

    for i, row in people_df.iterrows():
        norm = people_norm_names.iloc[i]
        if not norm or norm in ambiguous_norms:
            continue
        group = contact_groups.get(norm)
        if not group:
            continue

        existing_values = {str(row.get(c, "")).strip() for c in existing_email_cols if str(row.get(c, "")).strip() and str(row.get(c, "")).strip().lower() != "nan"}
        new_emails = [e for e in group["emails"] if e not in existing_values]
        if not new_emails:
            continue

        blank_slots = sum(1 for c in existing_email_cols if not str(row.get(c, "")).strip() or str(row.get(c, "")).strip().lower() == "nan")
        overflow = max(0, len(new_emails) - blank_slots)
        extra_columns_needed = max(extra_columns_needed, overflow)
        matched_plan[i] = new_emails

    new_email_cols = []
    if extra_columns_needed:
        last_n = max(int(EMAIL_COLUMN_PATTERN.match(c).group(1)) for c in existing_email_cols)
        for offset in range(1, extra_columns_needed + 1):
            col_name = f"email-{last_n + offset}"
            people_df[col_name] = ""
            people_df[col_name] = people_df[col_name].astype(object)
            new_email_cols.append(col_name)

    all_email_cols = existing_email_cols + new_email_cols

    # --- Pass 2: actually fill blanks, then overflow into the new columns, per row ---
    org_domains_filled = 0
    emails_filled = 0
    people_updated = set()

    for i, new_emails in matched_plan.items():
        norm = people_norm_names.iloc[i]
        group = contact_groups[norm]
        remaining = list(new_emails)

        for col in all_email_cols:
            if not remaining:
                break
            current = str(people_df.at[i, col]).strip()
            if not current or current.lower() == "nan":
                people_df.at[i, col] = remaining.pop(0)
                emails_filled += 1
                people_updated.add(i)

        current_org = str(people_df.at[i, "org_domain"]).strip()
        if group["org_domain"] and (not current_org or current_org.lower() == "nan"):
            people_df.at[i, "org_domain"] = group["org_domain"]
            org_domains_filled += 1
            people_updated.add(i)

    # --- Also fill org_domain for matched rows that had no NEW email but do have an org_domain gap ---
    for i, row in people_df.iterrows():
        if i in matched_plan:
            continue
        norm = people_norm_names.iloc[i]
        if not norm or norm in ambiguous_norms:
            continue
        group = contact_groups.get(norm)
        if not group or not group["org_domain"]:
            continue
        current_org = str(people_df.at[i, "org_domain"]).strip()
        if not current_org or current_org.lower() == "nan":
            people_df.at[i, "org_domain"] = group["org_domain"]
            org_domains_filled += 1
            people_updated.add(i)

    # --- Contacts that never matched any (non-ambiguous) Baserow person: append as new rows ---
    matched_norms = {people_norm_names.iloc[i] for i in range(len(people_df)) if people_norm_names.iloc[i]}
    unmatched_norms = [n for n in contact_groups if n not in matched_norms]

    appended_rows = []
    for norm in unmatched_norms:
        group = contact_groups[norm]
        new_row = {col: "" for col in people_df.columns}
        new_row[args.people_name_column] = group["raw_name"]
        for col, email in zip(all_email_cols, group["emails"]):
            new_row[col] = email
        new_row["org_domain"] = group["org_domain"]
        appended_rows.append(new_row)

    n_original_rows = len(people_df)
    if appended_rows:
        people_df = pd.concat([people_df, pd.DataFrame(appended_rows)], ignore_index=True)

    appended_row_indices = list(range(n_original_rows, n_original_rows + len(appended_rows)))

    # --- Write out, then apply yellow highlighting ---
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    people_df.to_excel(output_path, index=False)

    from openpyxl import load_workbook

    wb = load_workbook(output_path)
    ws = wb.active
    col_letter = {name: ws.cell(row=1, column=idx + 1).column_letter for idx, name in enumerate(people_df.columns)}

    # New columns: highlight header + every data cell
    new_columns = list(new_email_cols)
    if org_domain_is_new:
        new_columns.append("org_domain")
    for col_name in new_columns:
        letter = col_letter[col_name]
        for row_num in range(1, len(people_df) + 2):  # +1 for header, +1 for range end
            ws[f"{letter}{row_num}"].fill = YELLOW_FILL

    # Flagged rows (ambiguous names, appended unmatched contacts): highlight the whole row
    flagged_rows = set(ambiguous_row_indices) | set(appended_row_indices)
    for row_idx in flagged_rows:
        excel_row = row_idx + 2  # +1 for 0-index, +1 for header row
        for col_idx in range(1, len(people_df.columns) + 1):
            ws.cell(row=excel_row, column=col_idx).fill = YELLOW_FILL

    wb.save(output_path)

    print(f"Baserow People rows: {n_original_rows}")
    print(f"Rows updated with new data: {len(people_updated)}")
    print(f"Emails filled: {emails_filled}")
    print(f"org_domain values filled: {org_domains_filled}")
    print(f"New email columns created: {', '.join(new_email_cols) if new_email_cols else '(none)'}")
    print(f"org_domain column: {'newly created' if org_domain_is_new else 'already existed'}")
    print(f"Ambiguous duplicate-name People rows flagged (not filled): {len(ambiguous_row_indices)}")
    print(f"Unmatched contacts appended as new rows (flagged): {len(appended_rows)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
