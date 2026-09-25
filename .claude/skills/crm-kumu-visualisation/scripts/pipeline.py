#!/usr/bin/env python3
"""
CRM (Baserow) -> Kumu export pipeline.

Reads the five Baserow structure/data exports (People, Organisations,
Communities, Projects, Interactions), builds a Kumu-ready elements +
connections workbook, and writes TWO versions:

  kumu-import-internal-<date>.xlsx  - full data, real names, for RCM
                                       Cooperative's own internal Kumu map.
  kumu-import-public-<date>.xlsx    - consent-filtered, for the public map.
                                       People who haven't given public
                                       consent are excluded entirely;
                                       pseudonymised people get a stable
                                       hashed label and no identifiable
                                       profile fields.

Deterministic, pure Python (pandas + openpyxl) -- no LLM calls anywhere in
this pipeline, consistent with the other CRM skills (the privacy concern is
about exposing CRM data to a model's reasoning, not about code reading it).

Run from the repo root:

    python .claude/skills/crm-kumu-visualisation/scripts/pipeline.py

Input directory (default): private/kumu/baserow-export/
Output directory (default): private/kumu/kumu-input/
(Both resolved relative to the repo root you run this from, not relative to
this script's own location, per the "run from repo root, output alongside
input" convention used by the other CRM skills.)

See references/schema.md for the field/edge-type registry this pipeline
reads (config.py), and references/how-to-run.md for the full walkthrough,
known assumptions, and open questions flagged for review.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import os
import secrets
import sys
from datetime import date

import pandas as pd

import config


# ---------------------------------------------------------------------------
# Loading + validation
# ---------------------------------------------------------------------------

def find_input_file(input_dir: str, stub: str) -> str:
    pattern = os.path.join(input_dir, f"baserow-export-{stub}*.xlsx")
    matches = sorted(glob.glob(pattern))
    # Exclude Excel/Numbers lock files (e.g. "~$baserow-export-People-....xlsx"),
    # created while the real file is open elsewhere. These match the glob
    # pattern, aren't valid spreadsheet data, and (since "~" sorts after
    # letters) would otherwise be picked as the "most recent" match.
    matches = [m for m in matches if not os.path.basename(m).startswith("~$")]
    if not matches:
        raise FileNotFoundError(
            f"No input file found for '{stub}' matching {pattern}. "
            f"Expected a file named like 'baserow-export-{stub}-YYYYMMDD.xlsx'."
        )
    if len(matches) > 1:
        print(
            f"  note: multiple files matched '{stub}' "
            f"({[os.path.basename(m) for m in matches]}); using the last "
            f"(assumed most recent by filename): {os.path.basename(matches[-1])}"
        )
    return matches[-1]


def load_table(input_dir: str, stub: str) -> pd.DataFrame:
    path = find_input_file(input_dir, stub)
    try:
        df = pd.read_excel(path, sheet_name=0, dtype=str)
    except ValueError as e:
        raise ValueError(
            f"Could not read {os.path.basename(path)} as an Excel file ({e}). "
            f"If this file is currently open in Excel/Numbers, close it and "
            f"re-run -- an open file can leave a lock file behind, or the "
            f"save-in-progress version on disk can be briefly unreadable. "
            f"Otherwise confirm it was saved as .xlsx (not .xls or .numbers)."
        ) from e
    expected = set(config.EXPECTED_COLUMNS[stub])
    actual = set(df.columns)
    missing = expected - actual
    extra = actual - expected
    if missing:
        raise ValueError(
            f"Schema drift in {os.path.basename(path)}: missing expected "
            f"column(s) {sorted(missing)}. Update config.EXPECTED_COLUMNS "
            f"(and the edge/profile registries that reference them) to match "
            f"the current live Baserow schema before re-running."
        )
    if extra:
        print(
            f"  note: {os.path.basename(path)} has new column(s) not yet "
            f"registered in config.py: {sorted(extra)} -- ignored for now."
        )
    return df


def safe_str(value) -> str:
    """
    Like str(value).strip(), but treats pandas' NaN (a float, used for blank
    cells when a column is read with dtype=str) as empty rather than the
    literal string "nan". `value or ""` does NOT do this safely on its own
    -- NaN is truthy in Python, so `NaN or ""` evaluates to NaN, not "" --
    which was silently turning blank cells into the string "nan" wherever
    that pattern was used directly.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def split_multi(value) -> list[str]:
    """Baserow link-field cells export as a comma-separated list of labels."""
    value = safe_str(value)
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def join_pipe(values: list[str]) -> str:
    return "|".join(values)


# ---------------------------------------------------------------------------
# Pseudonymisation (stable across runs, not derivable without the salt file)
# ---------------------------------------------------------------------------

def load_or_create_salt(salt_path: str) -> str:
    if os.path.exists(salt_path):
        with open(salt_path, "r") as f:
            return f.read().strip()
    salt = secrets.token_hex(16)
    os.makedirs(os.path.dirname(salt_path), exist_ok=True)
    with open(salt_path, "w") as f:
        f.write(salt)
    print(f"  generated new pseudonymisation salt at {salt_path} (keep this file private and stable)")
    return salt


def pseudonymise(kumu_id: str, salt: str) -> str:
    digest = hashlib.sha256((salt + kumu_id).encode("utf-8")).hexdigest()[:8]
    return f"Person-{digest}"


# ---------------------------------------------------------------------------
# Build elements
# ---------------------------------------------------------------------------

def build_elements(tables: dict[str, pd.DataFrame], salt: str):
    """
    Returns:
      elements_internal: list[dict] - full data, real names
      elements_public:   list[dict] - consent-filtered
      label_maps: dict[type_name -> dict[label -> kumu_id]] (built from the
                  INTERNAL/real labels, since edge source data always refers
                  to real Baserow labels regardless of consent)
      person_status: dict[kumu_id -> "identifiable"|"pseudonymised"|"excluded"]
      warnings: list[str]
    """
    elements_internal = []
    elements_public = []
    label_maps: dict[str, dict[str, list[str]]] = {t: {} for t in config.NODE_TABLES}
    person_status: dict[str, str] = {}
    warnings: list[str] = []

    for type_name, spec in config.NODE_TABLES.items():
        df = tables[spec["file_stub"]]
        for _, row in df.iterrows():
            row_id = safe_str(row[spec["id_field"]])
            kumu_id = f"{type_name}-{row_id}"
            real_label = safe_str(row[spec["label_field"]])
            if not real_label:
                warnings.append(f"{type_name} row id={row_id} has an empty label -- skipped.")
                continue

            label_maps[type_name].setdefault(real_label, []).append(kumu_id)

            elem = {
                "ID": kumu_id,
                "Label": real_label,
                "Type": type_name,
                # Duplicate of "Type", used only for display (legend/shape/
                # color/filter). Kumu treats "Type" as a reserved structural
                # field (element de-duplication, default styling), which
                # gets in the way of customising legend formatting directly
                # -- same conflict as in the old MVP, same fix: drive display
                # off a separate "type-display" field and leave "Type" alone.
                "type-display": type_name,
                "Size": spec["size"],
            }
            display_field = config.TYPE_DISPLAY_SOURCE_FIELD.get(type_name)
            if display_field:
                display_value = safe_str(row.get(display_field))
                if display_value:
                    elem["type-display"] = display_value
                else:
                    warnings.append(
                        f"{type_name} row id={row_id} has no value in "
                        f"'{display_field}' -- type-display falls back to "
                        f"'{type_name}'."
                    )

            multiselect_fields = set(config.MULTISELECT_PROFILE_FIELDS.get(type_name, []))
            for field in config.PROFILE_FIELDS.get(type_name, []):
                if field in multiselect_fields:
                    elem[field] = join_pipe(split_multi(row.get(field)))
                else:
                    elem[field] = row.get(field, "")

            for field in config.INTERACTION_METADATA_FIELDS.get(type_name, []):
                elem[field] = join_pipe(split_multi(row.get(field)))
            # Unified cross-type interaction showcase field, mirroring the
            # old MVP's single "interaction-participant-all" -- since our
            # per-type interaction rollups have different field names
            # (interactions-lead/-participant on Person, -sponsor/-funder on
            # Organisation, plain "interactions" on Community/Project), Kumu
            # display settings can't point a single showcase control at any
            # one of them across all node types. This flattens whichever
            # ones apply to this type into one deduplicated list so a single
            # "interactions-all" showcase control works for every type.
            all_interactions: list[str] = []
            for field in config.INTERACTION_METADATA_FIELDS.get(type_name, []):
                all_interactions.extend(split_multi(row.get(field)))
            elem["interactions-all"] = join_pipe(sorted(set(all_interactions)))

            if spec["consent_field"]:
                consent = safe_str(row.get(spec["consent_field"]))
                elem["mapping-consent"] = consent
                elements_internal.append(dict(elem))

                if consent in config.CONSENT_INTERNAL_ONLY or not consent:
                    person_status[kumu_id] = "excluded"
                    continue  # not added to elements_public at all
                elif consent == config.CONSENT_PUBLIC_PSEUDONYMISED:
                    person_status[kumu_id] = "pseudonymised"
                    pub = dict(elem)
                    pub["Label"] = pseudonymise(kumu_id, salt)
                    for f in config.PERSON_IDENTIFIABLE_FIELDS:
                        pub[f] = ""
                    for f in config.PERSON_INTERNAL_ONLY_FIELDS:
                        pub[f] = ""
                    pub.pop("mapping-consent", None)
                    elements_public.append(pub)
                elif consent == config.CONSENT_PUBLIC_IDENTIFIABLE:
                    person_status[kumu_id] = "identifiable"
                    pub = dict(elem)
                    # PERSON_INTERNAL_ONLY_FIELDS (e.g. "notes") is stripped
                    # here too, unlike PERSON_IDENTIFIABLE_FIELDS -- consenting
                    # to appear under one's real name isn't the same as
                    # consenting to have arbitrary staff-written notes made
                    # public, so this tier is NOT otherwise redacted.
                    for f in config.PERSON_INTERNAL_ONLY_FIELDS:
                        pub[f] = ""
                    pub.pop("mapping-consent", None)
                    elements_public.append(pub)
                else:
                    warnings.append(
                        f"Person row id={row_id} has unrecognised mapping-consent "
                        f"value '{consent}' -- treated as excluded from public export."
                    )
                    person_status[kumu_id] = "excluded"
            else:
                # Non-Person types: always public, no consent field.
                elements_internal.append(dict(elem))
                elements_public.append(dict(elem))

    # Flag ambiguous (duplicate) labels within a single type -- these can't
    # be reliably resolved to a single ID when building edges below.
    for type_name, labels in label_maps.items():
        for label, ids in labels.items():
            if len(ids) > 1:
                warnings.append(
                    f"Ambiguous label '{label}' in {type_name}: matches {ids} -- "
                    f"edges naming this label will be skipped rather than guessed."
                )

    return elements_internal, elements_public, label_maps, person_status, warnings


# ---------------------------------------------------------------------------
# Build connections
# ---------------------------------------------------------------------------

def build_connections(tables: dict[str, pd.DataFrame], label_maps, person_status, warnings):
    connections = []
    counter = 0

    for source_type, field, target_type, edge_type in config.EDGE_FIELDS:
        source_spec = config.NODE_TABLES[source_type]
        df = tables[source_spec["file_stub"]]
        for _, row in df.iterrows():
            row_id = safe_str(row[source_spec["id_field"]])
            source_id = f"{source_type}-{row_id}"
            targets = split_multi(row.get(field))
            for target_label in targets:
                candidates = label_maps[target_type].get(target_label)
                if not candidates:
                    warnings.append(
                        f"{source_type} '{source_id}' field '{field}' names "
                        f"'{target_label}' -- no matching {target_type} found, edge skipped."
                    )
                    continue
                if len(candidates) > 1:
                    continue  # already warned about as an ambiguous label above
                target_id = candidates[0]
                counter += 1
                connections.append({
                    "ID": f"C{counter}",
                    "From": source_id,
                    "To": target_id,
                    "Type": edge_type,
                    "Direction": "undirected",
                })

    return connections


def filter_connections_for_public(connections: list[dict], person_status: dict) -> list[dict]:
    def excluded(kumu_id: str) -> bool:
        return person_status.get(kumu_id) == "excluded"

    return [
        c for c in connections
        if not excluded(c["From"]) and not excluded(c["To"])
    ]


# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------

def write_workbook(path: str, elements: list[dict], connections: list[dict]):
    elements_df = pd.DataFrame(elements)
    connections_df = pd.DataFrame(connections)
    # ID/Label/Type/type-display/Size first, then whatever profile columns exist.
    front = [c for c in ["ID", "Label", "Type", "type-display", "Size"] if c in elements_df.columns]
    rest = [c for c in elements_df.columns if c not in front]
    elements_df = elements_df[front + rest]

    conn_front = [c for c in ["ID", "From", "To", "Type", "Direction"] if c in connections_df.columns]
    conn_rest = [c for c in connections_df.columns if c not in conn_front]
    connections_df = connections_df[conn_front + conn_rest] if len(connections_df) else connections_df

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        elements_df.to_excel(writer, sheet_name="elements", index=False)
        connections_df.to_excel(writer, sheet_name="connections", index=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Build Kumu import workbooks from Baserow CRM exports.")
    parser.add_argument("--input-dir", default="private/kumu/baserow-export",
                         help="Directory containing the 5 baserow-export-*.xlsx exports.")
    parser.add_argument("--output-dir", default="private/kumu/kumu-input",
                         help="Directory to write the Kumu import workbooks to.")
    parser.add_argument("--date", default=date.today().strftime("%Y%m%d"),
                         help="Date tag for output filenames (default: today, YYYYMMDD).")
    args = parser.parse_args()

    print(f"Loading Baserow exports from {args.input_dir} ...")
    tables = {}
    for type_name, spec in {**config.NODE_TABLES, **config.NON_NODE_TABLES}.items():
        stub = spec["file_stub"]
        tables[stub] = load_table(args.input_dir, stub)
        print(f"  loaded {stub}: {len(tables[stub])} row(s)")

    salt_path = os.path.join(os.path.dirname(args.input_dir.rstrip("/")), "pseudonym-salt.txt")
    salt = load_or_create_salt(salt_path)

    print("Building elements ...")
    elements_internal, elements_public, label_maps, person_status, warnings = build_elements(tables, salt)

    print("Building connections ...")
    connections_internal = build_connections(tables, label_maps, person_status, warnings)
    connections_public = filter_connections_for_public(connections_internal, person_status)

    internal_path = os.path.join(args.output_dir, f"kumu-import-internal-{args.date}.xlsx")
    public_path = os.path.join(args.output_dir, f"kumu-import-public-{args.date}.xlsx")

    write_workbook(internal_path, elements_internal, connections_internal)
    write_workbook(public_path, elements_public, connections_public)

    print(f"\nWrote {len(elements_internal)} elements / {len(connections_internal)} connections -> {internal_path}")
    print(f"Wrote {len(elements_public)} elements / {len(connections_public)} connections -> {public_path}")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nNo warnings.")


if __name__ == "__main__":
    sys.exit(main())
