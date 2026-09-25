"""
parse_vcf.py

Parses a .vcf (vCard) file exported from Google Contacts / Google Takeout
into a flat CSV of (name, email) pairs.

No LLM involvement — this is pure structured text parsing using the
`vobject` library. One row is written per email address, so a contact
with two email addresses produces two rows sharing the same name.

An `org_domain` column is also produced: just the organisation-
identifying label of the contact's email domain, with the public suffix
stripped off (e.g. "Hdruk" from alice@hdruk.ac.uk, "UCL" from
alice@ucl.ac.uk) — the suffix itself (.ac.uk, .com, .nl, etc.) carries no
organisation-identifying information on its own. Extracted
deterministically via `tldextract` in offline mode (no live network
lookups — uses its bundled Public Suffix List snapshot, so results don't
silently change if that list updates mid-project). Left blank for known
personal/webmail domains (see PERSONAL_EMAIL_DOMAINS below) and for
contacts with no email. The label is capitalised for readability —
title-cased by default (e.g. "Stanford"), or fully upper-cased if it's in
the maintained KNOWN_ACRONYMS set (e.g. "UCL", "NHS") — but this is a raw
label, not a canonical organisation name; no attempt is made to map it to
an existing Baserow Organisations record, and case is cosmetic only, not
a matching key. That stays a human decision at review time.

(The vCard's own ORG: field is deliberately not read or output at all —
it was dropped as unreliable/mostly-blank on auto-collected contacts.)

Follows the observed export folder convention:

    private/email-contacts/all-contacts-<DATE>/all-contacts-<DATE>/*.vcf

where <DATE> is the export date as it appears in the folder name (e.g.
"20260905" for a folder called "all-contacts-20260905"). The inner folder
of the same name is Google Takeout's own archive-unzip nesting, kept as-is
rather than flattened, so the pipeline just looks one level deeper for it.

If you don't pass --input or --date, you'll be asked for the date
interactively.

Usage:
    # Resolve the .vcf automatically from the dated folder convention:
    python parse_vcf.py --date 20260905 --output parsed_contacts.csv

    # Or point at a specific file directly (bypasses the convention):
    python parse_vcf.py --input contacts.vcf --output parsed_contacts.csv

Requires:
    pip install vobject tldextract --break-system-packages
"""

import argparse
import csv
import glob
import re
import sys
from pathlib import Path

import tldextract
import vobject

DEFAULT_BASE_DIR = "private/email-contacts"

# Personal/webmail domains that shouldn't be treated as an organisation.
# Plain, easy to extend as new ones turn up in real data.
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "hotmail.com",
    "hotmail.co.uk",
    "outlook.com",
    "live.com",
    "msn.com",
    "icloud.com",
    "me.com",
    "mac.com",
    "yahoo.com",
    "yahoo.co.uk",
    "aol.com",
    "protonmail.com",
    "proton.me",
    "gmx.com",
    "mail.com",
    "zoho.com",
    "yandex.com",
}

# Offline mode: never fetches the Public Suffix List live over the network —
# uses tldextract's bundled snapshot instead, so this stays deterministic.
_tld_extractor = tldextract.TLDExtract(suffix_list_urls=())

# Known institution/organisation acronyms that should render fully upper-case
# rather than title-cased (e.g. "UCL" not "Ucl"). Matched case-insensitively
# against the extracted domain label. Plain, easy to extend as new ones turn
# up in real data — this is a readability/cosmetic list, not a matching key.
KNOWN_ACRONYMS = {
    "ucl", "lse", "ucla", "mit", "nhs", "bbc", "hdruk", "nih", "who",
    "oecd", "ukri", "nasa", "esa", "cern", "unesco", "unicef", "gchq",
    "hmrc", "dcms", "nsf", "fda", "cdc", "epsrc", "esrc", "bbsrc",
    "mrc", "nerc", "ahrc", "stfc", "wellcome",
}


def format_org_label(domain_label):
    """
    Capitalise a bare domain label for readability: fully upper-case if
    it's a known acronym (case-insensitive match against KNOWN_ACRONYMS,
    e.g. "ucl" -> "UCL"), otherwise title-cased (e.g. "stanford" ->
    "Stanford", "acme-widgets" -> "Acme-Widgets"). Cosmetic only — this
    does not change what the label matches against, if it's ever compared
    elsewhere; always compare/store the lower-cased form for that.
    """
    if not domain_label:
        return domain_label
    if domain_label.lower() in KNOWN_ACRONYMS:
        return domain_label.upper()
    return domain_label.title()


def extract_org_domain(email):
    """
    Return just the organisation-identifying label of an email's domain,
    capitalised for readability (e.g. "Hdruk" from alice@hdruk.ac.uk,
    "UCL" from alice@ucl.ac.uk — see format_org_label) — the public
    suffix (.ac.uk, .com, .nl, etc.) is stripped off, since it carries no
    organisation-identifying information on its own. Returns "" if the
    email is missing/malformed, or the domain is a known personal/webmail
    provider.
    """
    if not email or "@" not in email:
        return ""

    domain_part = email.rsplit("@", 1)[-1].strip().lower()
    if not domain_part:
        return ""

    extracted = _tld_extractor(domain_part)
    registered_domain = extracted.registered_domain.lower()

    if not registered_domain:
        return ""
    if registered_domain in PERSONAL_EMAIL_DOMAINS:
        return ""
    return format_org_label(extracted.domain.lower())


def prompt_for_date():
    """Ask the user for the export date, looping until it looks like YYYYMMDD."""
    while True:
        date_str = input(
            "Enter the export date as it appears in the folder name "
            "(e.g. 20260905 for 'all-contacts-20260905'): "
        ).strip()
        if re.fullmatch(r"\d{8}", date_str):
            return date_str
        print("That doesn't look like an 8-digit date (YYYYMMDD) — try again.")


def resolve_vcf_path(date_str, base_dir):
    """
    Find the .vcf file for a given export date, following the observed
    convention: base_dir/all-contacts-<date>/all-contacts-<date>/*.vcf
    (falling back to base_dir/all-contacts-<date>/*.vcf if the inner
    nested folder isn't present, in case a future export isn't
    double-nested the same way).
    """
    dated_folder_name = f"all-contacts-{date_str}"
    outer = Path(base_dir) / dated_folder_name
    inner = outer / dated_folder_name

    search_dirs_tried = []
    for candidate_dir in (inner, outer):
        search_dirs_tried.append(str(candidate_dir))
        matches = sorted(glob.glob(str(candidate_dir / "*.vcf")))
        if matches:
            return matches, search_dirs_tried

    return [], search_dirs_tried


def parse_vcf(vcf_path):
    """Read a .vcf file and yield dicts of {name, email, org_domain} per email found."""
    with open(vcf_path, "r", encoding="utf-8", errors="replace") as f:
        vcf_data = f.read()

    records = []
    skipped = 0

    for vcard in vobject.readComponents(vcf_data, ignoreUnreadable=True):
        name = ""

        if hasattr(vcard, "fn") and vcard.fn.value:
            name = vcard.fn.value.strip()

        emails = []
        for email_field in vcard.contents.get("email", []):
            if email_field.value:
                emails.append(email_field.value.strip())

        if not name and not emails:
            skipped += 1
            continue

        if not emails:
            # Contact has a name but no email at all — still worth flagging,
            # since it can't contribute to email-matching downstream.
            records.append({"name": name, "email": "", "org_domain": ""})
        else:
            for email in emails:
                records.append({"name": name, "email": email, "org_domain": extract_org_domain(email)})

    return records, skipped


def main():
    parser = argparse.ArgumentParser(description="Parse a Google Contacts .vcf export into CSV.")
    parser.add_argument("--input", help="Path to a specific .vcf file (bypasses the dated-folder convention)")
    parser.add_argument("--date", help="Export date as it appears in the folder name, e.g. 20260905 (used to locate the .vcf automatically)")
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR, help=f"Base folder the dated export folders live under (default: {DEFAULT_BASE_DIR})")
    parser.add_argument("--output", help="Path to write the output CSV (default: parsed_contacts_<date>.csv next to the resolved .vcf, if using --date)")
    args = parser.parse_args()

    vcf_path = args.input
    date_str = args.date

    if not vcf_path:
        if not date_str:
            date_str = prompt_for_date()

        matches, dirs_tried = resolve_vcf_path(date_str, args.base_dir)

        if not matches:
            print(
                f"No .vcf file found for date '{date_str}'. Looked in:\n  "
                + "\n  ".join(dirs_tried)
                + "\nPass --input to point at the file directly, or check the folder/date.",
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

    output_path = args.output
    if not output_path:
        if date_str:
            output_path = str(Path(args.base_dir) / f"all-contacts-{date_str}" / f"parsed_contacts_{date_str}.csv")
        else:
            # No --date given (a direct --input was used) — default to writing
            # alongside the input file, so output lands where the data came from.
            output_path = str(Path(vcf_path).parent / "parsed_contacts.csv")

    records, skipped = parse_vcf(vcf_path)

    if not records:
        print("No contact records found in the .vcf file. Nothing written.", file=sys.stderr)
        sys.exit(1)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "org_domain"])
        writer.writeheader()
        writer.writerows(records)

    no_email_count = sum(1 for r in records if not r["email"])
    org_domain_count = sum(1 for r in records if r["org_domain"])

    print(f"Parsed {len(records)} rows from {vcf_path}")
    print(f"  -> {no_email_count} contact(s) had no email address (kept, email left blank)")
    print(f"  -> {org_domain_count} row(s) got an org_domain value (personal/webmail domains excluded)")
    if skipped:
        print(f"  -> {skipped} vCard block(s) had neither a name nor an email and were skipped")
    print(f"Written to: {output_path}")


if __name__ == "__main__":
    main()
