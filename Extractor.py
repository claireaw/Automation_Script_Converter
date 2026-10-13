from __future__ import annotations

import csv
import math
import shlex
from pathlib import Path


CSV_FIELDS = [
    "source_log",
    "point_index",
    "VG_V",
    "VD_V",
    "VS_V",
    "ID_raw",
    "IG_raw",
    "IS_raw",
    "point_valid",
    "field_mapping_status",
]


class LogFormatError(ValueError):
    pass


def read_atlas_log(path: Path) -> list[dict[str, str]]:
    """Parse the observed f/p/d record layout; mapping remains provisional."""
    electrode_names: list[str] | None = None
    parameter_count: int | None = None
    data_records: list[list[float]] = []

    try:
        lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
    except (OSError, UnicodeError) as exc:
        raise LogFormatError(f"Could not read the selected file:\n{exc}") from exc

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parts = shlex.split(stripped)
        except ValueError as exc:
            raise LogFormatError(f"Malformed record on line {line_number}: {exc}") from exc

        if parts[0] == "f":
            if len(parts) < 2:
                raise LogFormatError(f"Malformed electrode metadata on line {line_number}")
            try:
                count = int(parts[1])
            except ValueError as exc:
                raise LogFormatError(f"Invalid electrode count on line {line_number}") from exc
            names = parts[2:]
            if len(names) != count:
                raise LogFormatError(
                    f"Electrode metadata on line {line_number} declares {count}, found {len(names)} names"
                )
            if electrode_names is not None and names != electrode_names:
                raise LogFormatError("The log contains conflicting electrode metadata")
            electrode_names = names
        elif parts[0] == "p":
            if len(parts) < 2:
                raise LogFormatError(f"Malformed parameter metadata on line {line_number}")
            try:
                parameter_count = int(parts[1])
            except ValueError as exc:
                raise LogFormatError(f"Invalid parameter count on line {line_number}") from exc
        elif parts[0] == "d":
            try:
                values = [float(value) for value in parts[1:]]
            except ValueError as exc:
                raise LogFormatError(f"Non-numeric data on line {line_number}") from exc
            if len(values) != 9:
                raise LogFormatError(
                    f"Data line {line_number} contains {len(values)} values; expected 9"
                )
            if not all(math.isfinite(value) for value in values):
                raise LogFormatError(f"Nonfinite value on data line {line_number}")
            data_records.append(values)

    if electrode_names != ["source", "drain", "gate"]:
        raise LogFormatError(
            "This version expects electrode metadata in the order source, drain, gate. "
            f"Found: {electrode_names!r}"
        )
    if parameter_count != 9:
        raise LogFormatError(f"Expected a 'p 9' metadata record; found {parameter_count!r}")
    if not data_records:
        raise LogFormatError("No numeric data records were found")

    rows: list[dict[str, str]] = []
    # Provisional interpretation: each electrode group is contact voltage,
    # applied voltage, terminal current. Keep only contact voltage and current
    # in the display/schema; do not present this as validated until compared to
    # an independent manual export.
    for point_index, values in enumerate(data_records):
        source = values[0:3]
        drain = values[3:6]
        gate = values[6:9]
        row = {
            "source_log": path.name,
            "point_index": str(point_index),
            "VG_V": f"{gate[0]:.12g}",
            "VD_V": f"{drain[0]:.12g}",
            "VS_V": f"{source[0]:.12g}",
            "ID_raw": f"{drain[2]:.12g}",
            "IG_raw": f"{gate[2]:.12g}",
            "IS_raw": f"{source[2]:.12g}",
            "point_valid": "UNKNOWN",
            "field_mapping_status": "PROVISIONAL_CONFIRM_WITH_REFERENCE_EXPORT",
        }
        rows.append(row)
    return rows


def main() -> None:
    print("ATLAS log value extractor")
    print("Field mapping is provisional; point convergence and current normalization are unverified.")
    print()
    raw_path = input("Paste the full path to an ATLAS .log file: ").strip().strip('"')
    if not raw_path:
        print("No log path entered. Exiting.")
        return

    try:
        input_path = Path(raw_path).expanduser()
        rows = read_atlas_log(input_path)
    except LogFormatError as exc:
        print(f"Could not extract values: {exc}")
        return

    print(f"\nLoaded {input_path} ({len(rows)} data points)\n")
    print(f"{'Point':>6} {'VG (V)':>14} {'VD (V)':>14} {'VS (V)':>14} {'ID raw':>16} {'IG raw':>16} {'IS raw':>16}")
    print("-" * 100)
    for row in rows:
        print(
            f"{int(row['point_index']):6d} "
            f"{float(row['VG_V']):14.7g} {float(row['VD_V']):14.7g} {float(row['VS_V']):14.7g} "
            f"{float(row['ID_raw']):16.7g} {float(row['IG_raw']):16.7g} {float(row['IS_raw']):16.7g}"
        )
    print("\nPoint validity: UNKNOWN for every row; this program does not check solver convergence.")

    save = input("\nSave these values to a CSV? [y/N]: ").strip().lower()
    if save not in {"y", "yes"}:
        print("Finished; no CSV written.")
        return

    default_path = input_path.with_name(input_path.stem + "_values.csv")
    output_text = input(f"CSV path [{default_path}]: ").strip().strip('"')
    output_path = Path(output_text).expanduser() if output_text else default_path
    try:
        with output_path.open("x", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    except FileExistsError:
        print(f"Refusing to overwrite existing CSV: {output_path}")
        return
    except OSError as exc:
        print(f"Could not write CSV: {exc}")
        return
    print(f"Saved {len(rows)} points to {output_path}")


if __name__ == "__main__":
    main()
