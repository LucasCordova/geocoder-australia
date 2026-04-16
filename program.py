from __future__ import annotations

import csv
from pathlib import Path

from geocoder import reverse_geocode


INPUT_PATH = Path("input_data.csv")
OUTPUT_PATH = Path("output_data.csv")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing {INPUT_PATH.resolve()}")

    rows_out: list[dict[str, str]] = []

    with INPUT_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "coordinates" not in reader.fieldnames:
            raise ValueError('input_data.csv must contain a "coordinates" column')

        for i, row in enumerate(reader, start=2):  # header is line 1
            coords = (row.get("coordinates") or "").strip()
            extras = row.get(None)  # when a row has more fields than the header
            if extras:
                coords = ",".join([coords, *[str(x).strip() for x in extras if str(x).strip()]])
            if not coords:
                continue

            try:
                suburb, postal_code = reverse_geocode(coords)
            except Exception as e:
                raise RuntimeError(f"Reverse geocode failed on line {i} ({coords!r}): {e}") from e

            rows_out.append(
                {
                    "coordinates": coords,
                    "suburb": suburb,
                    "postal_code": postal_code,
                }
            )

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["coordinates", "suburb", "postal_code"])
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    main()

