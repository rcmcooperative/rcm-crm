"""
pipeline.py

Single entrypoint for the crm-email-contacts pipeline. Wraps the three
stage scripts (parse_vcf.py, match_candidates.py, apply_matches.py) as
subcommands of one CLI, so the whole thing can be run and referred to as
one pipeline rather than three separate scripts.

Code only — no LLM. Each subcommand just calls the corresponding stage
script with the arguments you give it; nothing here does any matching or
parsing itself.

Usage:
    python pipeline.py parse   --input contacts.vcf --output parsed_contacts.csv
    python pipeline.py match   --contacts parsed_contacts.csv --people baserow-export-people-20260907.xlsx \
                                --people-name-column "name-person" --people-email-column "email-1" \
                                --output candidate_matches.xlsx
    # --- human review happens here, in candidate_matches.xlsx ---
    python pipeline.py apply   --people baserow-export-people-20260907.xlsx --candidates candidate_matches.xlsx \
                                --people-name-column "name-person" --people-email-column "email-1" \
                                --output people_export_updated.xlsx

Run `python pipeline.py <stage> --help` for a stage's full argument list.

Requires:
    pip install vobject pandas openpyxl --break-system-packages
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

STAGES = {
    "parse": "parse_vcf.py",
    "match": "match_candidates.py",
    "apply": "apply_matches.py",
    "fill": "fill_from_contacts.py",
}


def print_top_level_help():
    print("crm-email-contacts pipeline — code only, no LLM.\n")
    print("Usage: python pipeline.py <stage> [stage options]\n")
    print("Stages:")
    print("  parse   Parse a Google Contacts .vcf export into a plain CSV")
    print("  match   Fuzzy-match parsed contacts against a Baserow People export,")
    print("          producing a ranked candidate spreadsheet for human review")
    print("  apply   Write human-confirmed matches into a copy of the People export")
    print("  fill    Combined extraction+fill in one step: exact-name-match parsed")
    print("          contacts straight into a copy of the People export, no review")
    print("          spreadsheet — new columns and unmatched/ambiguous rows are")
    print("          highlighted yellow instead")
    print()
    print("'match' + 'apply' is the reviewed path (recommended for most runs).")
    print("'fill' is a faster, stricter-matching alternative with no review step —")
    print("see references/how-to-use.md for when each is appropriate.")
    print()
    print("Run 'python pipeline.py <stage> --help' for that stage's full options.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_top_level_help()
        sys.exit(0 if len(sys.argv) >= 2 else 1)

    stage = sys.argv[1]
    if stage not in STAGES:
        print(f"Unknown stage '{stage}'. Valid stages: {', '.join(STAGES)}\n")
        print_top_level_help()
        sys.exit(1)

    script_path = SCRIPTS_DIR / STAGES[stage]
    result = subprocess.run([sys.executable, str(script_path), *sys.argv[2:]])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
