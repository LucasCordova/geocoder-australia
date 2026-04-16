from __future__ import annotations

import csv
from pathlib import Path

from geocoder import reverse_geocode


INPUT_PATH = Path("trees-with-species-and-dimensions-urban-forest.csv")
OUTPUT_PATH = Path("output_data.csv")
FIELDNAMES = ["geolocation", "suburb", "postal_code"]


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing {INPUT_PATH.resolve()}")

    with (
        INPUT_PATH.open("r", newline="", encoding="utf-8") as fin,
        OUTPUT_PATH.open("w", newline="", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        if not reader.fieldnames or "geolocation" not in reader.fieldnames:
            raise ValueError('input_data.csv must contain a "geolocation" column')

        writer = csv.DictWriter(fout, fieldnames=FIELDNAMES)
        writer.writeheader()
        fout.flush()

        for i, row in enumerate(reader, start=2):  # header is line 1
            coords = (row.get("geolocation") or "").strip()
            extras = row.get(None)
            if extras:
                coords = ",".join([coords, *[str(x).strip() for x in extras if str(x).strip()]])
            if not coords:
                continue

            try:
                suburb, postal_code = reverse_geocode(coords)
            except Exception as e:
                raise RuntimeError(f"Reverse geocode failed on line {i} ({coords!r}): {e}") from e

            writer.writerow(
                {
                    "geolocation": coords,
                    "suburb": suburb,
                    "postal_code": postal_code,
                }
            )
            fout.flush()


if __name__ == "__main__":
    main()
