#!/usr/bin/env python3
"""
run_pipeline.py — single-command, no-LLM pipeline for crm-slack-extraction.

Purpose
-------
Runs the entire skill end to end with one command, no Claude Code /
claude-local / claude-cloud session involved at any point. This exists
because the only step that was ever manual (filling in `type`,
`name-interaction-long`, and matching Slack users to existing People
rows in candidates-<date>.csv) turned out to require no judgement at
all — every part of it is a fixed value or a deterministic email
lookup. Folding it in here removes the last reason to open an LLM
session to run this skill in its current, code-only scope (see
SKILL.md's "Parked features" for what's *not* included and why).

Every run is identified by the Slack export's date, in ISO YYYYMMDD
format (e.g. 20260907) — not an arbitrary name. This matches the
export folder convention: private/slack/slack-export-<yyyymmdd>/.
Every output filename derives from the same date, so re-running for a
different export date never overwrites another date's output.

What this script does, in order:

1. Determines the export date — from --date if given, otherwise
   prompts for it interactively. Validates it's exactly 8 digits
   before doing anything else.
2. Derives the export directory (private/slack/slack-export-<date>/)
   unless --export-dir overrides it.
3. If the channel-mapping CSV doesn't exist yet at the given path,
   generates a starter one: one row per channel found in
   channels.json, mapping pre-filled as "standalone" (the common case
   for a public topic/community channel — see references/how-to-run.md's
   "First run" section for when a channel should instead map to an
   existing Interaction). The script then stops so a human can review
   and edit it before anything is written to the CRM — it never
   proceeds past an auto-generated, unreviewed mapping.
4. Loads users.json, channels.json, and the channel-mapping CSV
   (reusing the exact same functions parse_slack_export.py uses, by
   importing from it — no logic is duplicated between the two files).
5. Stops with a clear error if any channel is missing from either the
   export or the mapping CSV (same check as parse_slack_export.py).
6. Optionally loads a People-table export CSV (see --people-export)
   and matches each channel member's Slack email against it. A match
   uses the existing person's canonical name-person; a non-match uses
   the Slack real_name/name instead, AND is written to a separate
   flagged-unmatched-users-<date>.csv for a human to resolve later —
   this script never invents or skips a participant, it just flags
   which ones it couldn't confirm against the live CRM.
6a. Builds a full People-table candidate list: every unique Slack user
   (deleted/bot accounts already excluded) found across EVERY mapped
   channel — both standalone and existing-Interaction ones, since the
   point here is finding people who might be new to the CRM at all,
   not just participants of new Interactions. Deliberately makes NO
   attempt to exclude people who already exist in the CRM — see
   "Known limitation" below.
7. For every STANDALONE channel (per the mapping CSV), writes a
   complete Interactions row to candidates-<date>.csv: type,
   name-interaction-long, people-participants, date-started,
   date-last-activity. Channels mapping to an existing Interaction are
   still excluded from this file, same as before — this script has no
   access to the live Baserow row to know which one to extend, so
   those are listed in the printed summary for a human to update the
   notes field of by hand. The People rows from step 6a are written to
   the same candidates-<date>.csv, ahead of the Interactions rows.
8. Runs build_workbook.py on the resulting candidates-<date>.csv to
   produce the final xlsx.
9. Adds one extra worksheet per standalone channel to that xlsx, each
   a plain single-column list of that channel's participants in
   alphabetical order — meant purely to be easy to select and
   copy/paste into Baserow, as an alternative to reading names out of
   the semicolon-separated people-participants cell on the main
   Interactions sheet.

Nothing in this script reads message content, computes per-user
activity counts, or calls any model/API — see SKILL.md's "Parked
features" for the two pieces of analysis that were deliberately left
out and why.

Known limitation — no existing-CRM dedup check
------------------------------------------------
The People-table candidate list (step 6a above) is built purely from
the Slack export, with no attempt to check whether a given person
already has a row in the live Baserow People table — even the
--people-export email match (used only for naming Interaction
participants, see step 6) is not applied here to filter this list.
Every unique, non-bot, non-deleted Slack user found across the mapped
channels is written as a candidate, including people already in the
CRM. Checking against the live CRM would need either a full People
export cross-reference (fragile — stale the moment someone's added
after the export) or a live Baserow API query per person (not
implemented). A live API check is a reasonable next step if this
becomes a recurring, larger-scale run — not built now.

Usage
-----
    python3 run_pipeline.py [--date YYYYMMDD] [--export-dir <dir>] [--channel-mapping <csv>] [--people-export <csv>]

Normally --date is the only argument you need to pass — every other
path is derived from it, matching the private/slack/slack-export-<date>/
convention:

- --date: the Slack export's date, ISO YYYYMMDD (e.g. 20260907). If
  omitted, the script prompts for it.
- --export-dir (optional): overrides the derived
  private/slack/slack-export-<date>/ path.
- --channel-mapping (optional): overrides the derived
  private/slack/slack-export-<date>/channel-mapping-<date>.csv path.
  Conventionally lives INSIDE the export folder itself — not at the
  private/ top level. All outputs (candidates CSV, flagged-users CSV,
  final xlsx) are written alongside wherever this file ends up, so
  keeping it inside the export folder keeps each date's inputs and
  outputs together in one place.
- --people-export (optional): overrides the derived
  private/slack/slack-export-<date>/people-export.csv path. A CSV
  export of the live People table, with at least name-person,
  email-1, email-2 columns (matching references/schema.md's column
  names). If neither this nor a file at the derived default path
  exists, the pipeline runs without People-table matching — every
  channel member is written using their Slack name and flagged as
  unmatched.

Outputs (written alongside the channel-mapping CSV — i.e. inside the
export folder, per the convention above)
------------------------------------------------------------------
- candidates-<date>.csv
- flagged-unmatched-users-<date>.csv (only written if there's at least
  one unmatched user)
- crm-extraction-output-<date>.xlsx (via build_workbook.py)
"""

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_slack_export import (  # noqa: E402
    VALID_MAPPING_STANDALONE,
    channel_date_range,
    find_mismatches,
    load_channel_mapping,
    load_channels,
    load_users,
)

BUILD_WORKBOOK = Path(__file__).resolve().parent / "build_workbook.py"

DATE_PATTERN = re.compile(r"^\d{8}$")


def prompt_for_date():
    """Interactively prompts for the export date, re-prompting until a
    valid 8-digit YYYYMMDD string is entered."""
    while True:
        entered = input("Slack export date (ISO YYYYMMDD, e.g. 20260907): ").strip()
        if DATE_PATTERN.match(entered):
            return entered
        print(f"  '{entered}' isn't 8 digits in YYYYMMDD form — try again.")


def validate_date(date_str):
    """Raises ValueError with a clear message if date_str isn't a
    valid 8-digit YYYYMMDD string."""
    if not DATE_PATTERN.match(date_str):
        raise ValueError(
            f"--date must be exactly 8 digits in ISO YYYYMMDD form (e.g. 20260907); "
            f"got '{date_str}'."
        )


def load_people_export(people_csv_path):
    """Returns {normalized_email: name_person}, built from a live
    People-table export. Expects at least name-person, email-1,
    email-2 columns — see references/schema.md for the canonical
    column names. Returns an empty dict if people_csv_path is None,
    in which case every member is treated as unmatched."""
    if people_csv_path is None:
        return {}

    lookup = {}
    with open(people_csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name-person") or "").strip()
            if not name:
                continue
            for email_col in ("email-1", "email-2"):
                email = (row.get(email_col) or "").strip().lower()
                if email:
                    lookup[email] = name
    return lookup


def match_channel_members(member_ids, users, people_lookup):
    """Returns (participant_names, unmatched_records).

    participant_names: list of display names to write into
    people-participants — a live-CRM name where matched, otherwise the
    person's Slack real_name/name.

    unmatched_records: list of dicts describing every member who
    couldn't be matched against people_lookup, for the flagged-items
    file. Empty if --people-export wasn't given at all, only skipped
    for genuinely deleted/bot accounts (already filtered out of
    `users` before this function is called).
    """
    participant_names = []
    unmatched_records = []

    for uid in member_ids:
        info = users.get(uid)
        if info is None:
            continue  # deleted/bot account — not a candidate at all

        slack_display_name = info.get("real_name") or info.get("name") or uid
        email = (info.get("email") or "").strip().lower()
        matched_name = people_lookup.get(email) if email else None

        if matched_name:
            participant_names.append(matched_name)
        else:
            participant_names.append(slack_display_name)
            unmatched_records.append({
                "slack_id": uid,
                "slack_name": slack_display_name,
                "email": info.get("email", ""),
            })

    return participant_names, unmatched_records


def split_name(full_name):
    """Splits a Slack real_name/name into (first, last) on the first
    whitespace — a simple heuristic, not name-parsing intelligence.
    A single-token name (e.g. just a first name, or a handle with no
    space) returns (name, ""). Never guesses a last name that isn't
    there."""
    parts = full_name.strip().split(None, 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], ""
    return "", ""


def build_people_candidates(mapping, channel_members, users):
    """Returns a list of {"real_name":, "email":} dicts: one per
    unique Slack user (deleted/bot accounts already excluded via
    `users`) found across EVERY channel in the mapping — standalone
    AND existing-Interaction channels alike, since the goal here is
    finding people who might not be in the CRM at all yet, independent
    of which Interactions get written. Deduplicated by Slack user ID.
    Sorted alphabetically by name for a readable sheet.

    Deliberately does NOT filter out anyone already matched against
    --people-export — this is a full, unfiltered candidate list. See
    the module docstring's "Known limitation" section for why."""
    seen_ids = set()
    candidates = []

    for channel in mapping:
        for uid in channel_members.get(channel, []):
            if uid in seen_ids:
                continue
            info = users.get(uid)
            if info is None:
                continue  # deleted/bot account — already excluded from `users`
            seen_ids.add(uid)
            candidates.append({
                "real_name": info.get("real_name") or info.get("name") or uid,
                "email": info.get("email", ""),
            })

    candidates.sort(key=lambda c: c["real_name"].casefold())
    return candidates


def write_candidates(output_path, mapping, channel_dates, channel_members, users, people_lookup, people_candidates):
    """Writes candidates-<date>.csv in full: first every People
    candidate row (see build_people_candidates), then a complete
    Interactions row (type, name-interaction-long, people-participants,
    date-started, date-last-activity) for every STANDALONE channel.
    Returns (all_unmatched, channel_participants):

    all_unmatched: unmatched-user records across every channel, keyed
    by channel name, for the flagged-items file.

    channel_participants: {channel: [participant names]} for every
    STANDALONE channel, for add_participant_tabs() to build the
    per-channel copy/paste tabs from — same names written to
    people-participants above, just also handed back separately so
    the tab-building step doesn't need to re-derive them.
    """
    all_unmatched = {}
    channel_participants = {}

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["table", "row", "column", "value"])

        for row_num, person in enumerate(people_candidates, start=1):
            first, last = split_name(person["real_name"])
            if first:
                writer.writerow(["People", row_num, "name-person-first", first])
            if last:
                writer.writerow(["People", row_num, "name-person-last", last])
            if person["email"]:
                writer.writerow(["People", row_num, "email-1", person["email"]])

        row_num = 1
        for channel, mapping_value in mapping.items():
            if mapping_value != VALID_MAPPING_STANDALONE:
                continue  # existing-Interaction case — flagged in the run summary instead

            member_ids = channel_members.get(channel, [])
            participant_names, unmatched = match_channel_members(member_ids, users, people_lookup)
            if unmatched:
                all_unmatched[channel] = unmatched
            channel_participants[channel] = participant_names

            earliest, latest = channel_dates.get(channel, (None, None))

            writer.writerow(["Interactions", row_num, "type", "slack-channel"])
            writer.writerow(["Interactions", row_num, "name-interaction-long", channel])
            if participant_names:
                writer.writerow([
                    "Interactions", row_num, "people-participants",
                    "; ".join(participant_names),
                ])
            if earliest:
                writer.writerow(["Interactions", row_num, "date-started", earliest])
            if latest:
                writer.writerow(["Interactions", row_num, "date-last-activity", latest])

            row_num += 1

    return all_unmatched, channel_participants


def sanitize_sheet_title(name, existing_titles):
    """Returns an Excel-safe, unique worksheet title derived from a
    channel name: strips characters Excel forbids in sheet titles
    (: \\ / ? * [ ]), truncates to Excel's 31-character limit, and
    appends a numeric suffix if the result collides with a title
    that's already been used (either an existing sheet in the
    workbook, or another channel's title earlier in this same run)."""
    forbidden = set(r'\/?*[]:')
    cleaned = "".join(ch for ch in name if ch not in forbidden).strip()
    if not cleaned:
        cleaned = "channel"
    base = cleaned[:31]

    title = base
    suffix = 2
    while title in existing_titles:
        suffix_str = f" ({suffix})"
        title = base[: 31 - len(suffix_str)] + suffix_str
        suffix += 1

    existing_titles.add(title)
    return title


def add_participant_tabs(xlsx_path, channel_participants):
    """Adds one worksheet per standalone channel to the already-built
    workbook, each listing that channel's participants one per row,
    alphabetically — a plain, single-column list meant to be easy to
    select and copy/paste straight into Baserow, as an alternative to
    reading them out of the semicolon-separated people-participants
    cell on the main Interactions sheet."""
    import openpyxl
    from openpyxl.styles import Font

    wb = openpyxl.load_workbook(xlsx_path)
    existing_titles = set(wb.sheetnames)

    for channel in sorted(channel_participants):
        participants = channel_participants[channel]
        if not participants:
            continue  # nothing to list — skip rather than add an empty tab

        title = sanitize_sheet_title(channel, existing_titles)
        ws = wb.create_sheet(title=title)
        ws.append(["Name"])
        ws["A1"].font = Font(bold=True)
        for name in sorted(participants, key=str.casefold):
            ws.append([name])
        ws.column_dimensions["A"].width = max(24, len(channel) + 4)

    wb.save(xlsx_path)


def write_flagged_unmatched(output_path, all_unmatched):
    """Writes one row per unmatched user per channel. Only called if
    there's at least one unmatched user across the whole run."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["channel", "slack_id", "slack_name", "email"])
        for channel, records in all_unmatched.items():
            for r in records:
                writer.writerow([channel, r["slack_id"], r["slack_name"], r["email"]])


def write_starter_mapping(output_path, channels):
    """Writes a starter channel-mapping CSV: one row per channel found
    in channels.json, sorted alphabetically, with mapping pre-filled
    as 'standalone' — the common case for a public topic/community
    channel that isn't the Slack side of one specific, already-tracked
    relationship. See references/how-to-run.md's "First run" section
    for when to change a specific row to an existing Interaction's
    name instead."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["channel", "mapping"])
        for channel_name in sorted(channels):
            writer.writerow([channel_name, VALID_MAPPING_STANDALONE])


def main():
    parser = argparse.ArgumentParser(
        description="Run the full crm-slack-extraction pipeline with no LLM step."
    )
    parser.add_argument(
        "--date", default=None,
        help="Slack export date, ISO YYYYMMDD (e.g. 20260907). Prompted for if omitted. "
             "This is normally the only argument you need to pass — every path below is "
             "derived from it unless explicitly overridden.",
    )
    parser.add_argument(
        "--export-dir", type=Path, default=None,
        help="Overrides the derived private/slack/slack-export-<date>/ path.",
    )
    parser.add_argument(
        "--channel-mapping", type=Path, default=None, dest="channel_mapping_csv",
        help="Overrides the derived "
             "private/slack/slack-export-<date>/channel-mapping-<date>.csv path.",
    )
    parser.add_argument(
        "--people-export", type=Path, default=None,
        help="Overrides the derived private/slack/slack-export-<date>/people-export.csv "
             "path. If that default file doesn't exist and this isn't given either, the "
             "pipeline runs without People-table matching — every member is flagged as "
             "unmatched.",
    )
    args = parser.parse_args()

    date_str = args.date if args.date is not None else prompt_for_date()
    try:
        validate_date(date_str)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    export_dir = args.export_dir if args.export_dir is not None else Path(f"private/slack/slack-export-{date_str}")

    if not export_dir.is_dir():
        print(f"ERROR: export directory not found: {export_dir}", file=sys.stderr)
        sys.exit(1)

    channel_mapping_csv = (
        args.channel_mapping_csv if args.channel_mapping_csv is not None
        else export_dir / f"channel-mapping-{date_str}.csv"
    )

    if args.people_export is not None:
        people_export = args.people_export
        if not people_export.exists():
            print(f"ERROR: --people-export file not found: {people_export}", file=sys.stderr)
            sys.exit(1)
    else:
        default_people_export = export_dir / "people-export.csv"
        people_export = default_people_export if default_people_export.exists() else None

    channels = load_channels(export_dir)

    if not channel_mapping_csv.exists():
        write_starter_mapping(channel_mapping_csv, channels)
        print(f"No channel-mapping CSV found — created a starter one at {channel_mapping_csv}")
        print(f"  {len(channels)} channel(s) listed, all pre-filled as 'standalone'.")
        print(
            "  Review it: change any channel that's really the Slack side of an existing "
            "Interaction to that Interaction's exact name instead of 'standalone' — see "
            "references/how-to-run.md's \"First run\" section for when that applies."
        )
        print("  Then re-run this same command.")
        sys.exit(0)

    try:
        mapping = load_channel_mapping(channel_mapping_csv)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    users = load_users(export_dir)
    people_lookup = load_people_export(people_export)

    mismatches = find_mismatches(mapping, channels, export_dir)
    if mismatches:
        print("ERROR: channel-mapping CSV and export contents don't line up:", file=sys.stderr)
        for m in mismatches:
            print(f"  - {m}", file=sys.stderr)
        print("\nFix the mismatch and re-run. No output was written.", file=sys.stderr)
        sys.exit(1)

    channel_dates = {}
    channel_members = {}
    for channel_name in mapping:
        channel_dir = export_dir / channel_name
        channel_dates[channel_name] = channel_date_range(channel_dir)
        channel_members[channel_name] = channels[channel_name].get("members", [])

    output_dir = channel_mapping_csv.parent
    candidates_path = output_dir / f"candidates-{date_str}.csv"
    xlsx_path = output_dir / f"crm-extraction-output-{date_str}.xlsx"
    flagged_path = output_dir / f"flagged-unmatched-users-{date_str}.csv"

    people_candidates = build_people_candidates(mapping, channel_members, users)
    all_unmatched, channel_participants = write_candidates(
        candidates_path, mapping, channel_dates, channel_members, users, people_lookup,
        people_candidates,
    )

    standalone_channels = [c for c, v in mapping.items() if v == VALID_MAPPING_STANDALONE]
    existing_interaction_channels = {c: v for c, v in mapping.items() if v != VALID_MAPPING_STANDALONE}

    print(
        f"OK: {len(mapping)} channel(s) processed for export date {date_str} "
        f"({len(standalone_channels)} standalone, {len(existing_interaction_channels)} folding into existing Interactions)."
    )
    print(f"  wrote {candidates_path}")
    print(
        f"  {len(people_candidates)} People candidate(s) written from Slack — no existing-CRM "
        "dedup applied (see run_pipeline.py's \"Known limitation\")"
    )

    if all_unmatched:
        write_flagged_unmatched(flagged_path, all_unmatched)
        total_unmatched = sum(len(v) for v in all_unmatched.values())
        print(f"  wrote {flagged_path} ({total_unmatched} unmatched user(s) across {len(all_unmatched)} channel(s))")
        if people_export is None:
            print("  (no people-export.csv found or given, so every member is unmatched by definition)")
    else:
        print("  no unmatched users" + ("" if people_export is not None else " (no people-export.csv found or given)"))

    if existing_interaction_channels:
        print("\n  Channels folding into an existing Interaction (not written to candidates — update these by hand):")
        for channel, target in existing_interaction_channels.items():
            print(f"    - '{channel}' -> {target}")

    print(f"\nRunning build_workbook.py -> {xlsx_path}")
    result = subprocess.run(
        [sys.executable, str(BUILD_WORKBOOK), str(candidates_path), str(xlsx_path)],
    )
    if result.returncode != 0:
        print("ERROR: build_workbook.py failed — see its output above.", file=sys.stderr)
        sys.exit(result.returncode)

    add_participant_tabs(xlsx_path, channel_participants)
    tab_count = sum(1 for v in channel_participants.values() if v)
    print(f"  added {tab_count} per-channel participant tab(s) to {xlsx_path}, alphabetical, for copy/paste into Baserow")


if __name__ == "__main__":
    main()
