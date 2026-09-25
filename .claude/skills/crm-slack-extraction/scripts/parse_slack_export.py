#!/usr/bin/env python3
"""
parse_slack_export.py — deterministic first pass over a Slack Standard
Export, for RCM Cooperative's crm-slack-extraction skill.

Purpose
-------
Pure computation — no model reasoning, and (see "Parked features" in
SKILL.md) no per-user activity analysis and no reading of message
content at all. This script reads only:

- users.json (for identity matching)
- channels.json (for channel membership)
- the FILENAMES of each channel's per-day message files (for the
  channel's active date range) — it never opens or reads the content
  of those files.

It:

1. Builds a Slack user ID -> {name, email} lookup, filtering out
   deactivated accounts and bots.
2. For every channel listed in the channel-mapping CSV, treats channel
   *membership* as participation (Cass's explicit decision — no
   minimum-activity floor, and no per-user activity metric of any
   kind is computed).
3. Determines each channel's date-started / date-last-activity from
   the earliest and latest YYYY-MM-DD.json filename present in that
   channel's export folder.
4. Writes a skeleton candidates-<name>.csv, in the same
   table,row,column,value format build_workbook.py expects, pre-filled
   with only what's fully computable without judgement:
   people-participants and the two date fields, one row per
   STANDALONE channel. Channels mapping to an existing Interaction are
   deliberately NOT written here — this script has no access to the
   live CRM to know which row to extend, so SKILL.md Step 2 flags
   those for Cass to handle by hand.

Lead-status signals (message/thread/reaction counts) and discussion
summaries were both designed and then deliberately parked before
implementation — see "Parked features" in SKILL.md for why. This
script does not compute either, and does not open any message file's
contents for any purpose.

This script does not call any model, external API, or web service.

Usage
-----
    python3 parse_slack_export.py <export_dir> <channel_mapping.csv> <name>

- export_dir: path to the unzipped Slack Standard Export folder,
  containing users.json, channels.json, and one subfolder per channel.
- channel_mapping.csv: two columns, header row required: channel,mapping
  - channel: the channel's name, exactly as it appears in channels.json
    and as its export subfolder is named.
  - mapping: either an existing Interaction's name (this channel's
    activity folds into that Interaction's notes — see SKILL.md Step 2)
    or the literal value "standalone" (gets its own slack-channel
    Interaction row).
- name: used to derive the output filename, written into the same
  directory as channel_mapping.csv — e.g. name="funding-q3" produces
  candidates-funding-q3.csv.

Every channel named in channel_mapping.csv MUST have a matching
subfolder in export_dir and a matching entry in channels.json, or the
script stops with an error naming the exact mismatch — it does not
skip a channel silently. Likewise, if the export contains a public
channel that ISN'T in channel_mapping.csv, the script stops and lists
it — SKILL.md Step 2 requires every channel be explicitly mapped
before a run, not defaulted either way.
"""

import csv
import json
import re
import sys
from pathlib import Path

VALID_MAPPING_STANDALONE = "standalone"

DAY_FILE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\.json$")


def load_users(export_dir):
    """Returns {user_id: {"name": ..., "real_name": ..., "email": ...}},
    skipping deleted accounts and bots entirely."""
    users_path = export_dir / "users.json"
    with open(users_path, encoding="utf-8") as f:
        raw_users = json.load(f)

    users = {}
    for u in raw_users:
        if u.get("deleted") or u.get("is_bot"):
            continue
        profile = u.get("profile", {}) or {}
        users[u["id"]] = {
            "name": u.get("name", ""),
            "real_name": u.get("real_name", ""),
            "email": profile.get("email", ""),
        }
    return users


def load_channels(export_dir):
    """Returns {channel_name: channel_dict} straight from channels.json."""
    channels_path = export_dir / "channels.json"
    with open(channels_path, encoding="utf-8") as f:
        raw_channels = json.load(f)
    return {c["name"]: c for c in raw_channels}


def load_channel_mapping(mapping_path):
    """Returns {channel_name: mapping_value}, in file order."""
    mapping = {}
    with open(mapping_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        required = {"channel", "mapping"}
        missing = required - fieldnames
        if missing:
            raise ValueError(
                "channel-mapping CSV is missing required header column(s): "
                f"{', '.join(sorted(missing))}. Header row must be exactly: channel,mapping"
            )
        for line in reader:
            channel = (line.get("channel") or "").strip()
            value = (line.get("mapping") or "").strip()
            if not channel:
                continue
            mapping[channel] = value
    return mapping


def find_mismatches(mapping, channels, export_dir):
    """Returns a list of error strings for any channel present in one
    place (mapping CSV / channels.json / export folder) but not the
    others. Empty list means everything lines up and it's safe to
    proceed."""
    errors = []

    mapped_names = set(mapping)
    export_names = set(channels)

    for name in sorted(mapped_names - export_names):
        errors.append(
            f"'{name}' is listed in the channel-mapping CSV but has no "
            "matching entry in channels.json — check for a typo, or a "
            "channel that isn't in this export."
        )

    for name in sorted(export_names - mapped_names):
        errors.append(
            f"'{name}' exists in this export's channels.json but is not "
            "listed in the channel-mapping CSV — every exported channel "
            f"must be explicitly mapped (to an existing Interaction, or "
            f"'{VALID_MAPPING_STANDALONE}') before this script will "
            "proceed. See SKILL.md Step 2."
        )

    for name in mapping:
        if name not in channels:
            continue  # already reported above
        channel_dir = export_dir / name
        if not channel_dir.is_dir():
            errors.append(
                f"'{name}' has a channels.json entry and a mapping-CSV row, "
                f"but no matching folder was found at {channel_dir} — "
                "the export may be incomplete."
            )

    return errors


def channel_date_range(channel_dir):
    """Returns (earliest_date_str, latest_date_str) or (None, None) if
    no day-files are present. Reads ONLY filenames — never opens or
    parses any day-file's content. Dates are the YYYY-MM-DD each
    day-file is named after, i.e. a date on which at least one message
    was sent in that channel."""
    dates = []
    for entry in channel_dir.iterdir():
        if not entry.is_file():
            continue
        match = DAY_FILE_PATTERN.match(entry.name)
        if match:
            dates.append(match.group(1))

    if not dates:
        return None, None
    return min(dates), max(dates)


def write_candidates_skeleton(output_path, mapping, channel_dates, channel_members, users):
    """Writes only what's fully computable without judgement:
    people-participants and the two date fields, one Interactions row
    per STANDALONE channel. See module docstring for why
    existing-Interaction-mapped channels are excluded here."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["table", "row", "column", "value"])

        row_num = 1
        for channel, mapping_value in mapping.items():
            if mapping_value != VALID_MAPPING_STANDALONE:
                continue  # existing-Interaction case — handled by hand, see SKILL.md Step 2

            member_ids = channel_members.get(channel, [])
            participant_names = []
            for uid in member_ids:
                info = users.get(uid)
                if info is None:
                    continue  # deleted/bot account, already filtered — not a candidate
                participant_names.append(info["real_name"] or info["name"])

            earliest, latest = channel_dates.get(channel, (None, None))

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


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 parse_slack_export.py <export_dir> <channel_mapping.csv> <name>",
            file=sys.stderr,
        )
        sys.exit(1)

    export_dir = Path(sys.argv[1])
    mapping_path = Path(sys.argv[2])
    name = sys.argv[3]

    if not export_dir.is_dir():
        print(f"ERROR: export directory not found: {export_dir}", file=sys.stderr)
        sys.exit(1)
    if not mapping_path.exists():
        print(f"ERROR: channel-mapping CSV not found: {mapping_path}", file=sys.stderr)
        sys.exit(1)

    try:
        mapping = load_channel_mapping(mapping_path)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    users = load_users(export_dir)
    channels = load_channels(export_dir)

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

    output_dir = mapping_path.parent
    candidates_path = output_dir / f"candidates-{name}.csv"

    write_candidates_skeleton(candidates_path, mapping, channel_dates, channel_members, users)

    total_channels = len(mapping)
    standalone_count = sum(1 for v in mapping.values() if v == VALID_MAPPING_STANDALONE)
    print(
        f"OK: processed {total_channels} channel(s) "
        f"({standalone_count} standalone, "
        f"{total_channels - standalone_count} folding into existing Interactions)."
    )
    print(f"  wrote {candidates_path} (skeleton — extend per SKILL.md Step 3 before running build_workbook.py)")
    print(
        "  note: no per-user activity counts or message content were read — "
        "see SKILL.md 'Parked features'."
    )


if __name__ == "__main__":
    main()
