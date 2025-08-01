#!/usr/bin/env python3
"""
clean_socials.py
Extracts selected URL sections from a raw PhoneInfoga result file and saves
them as structured JSON.

Usage examples
--------------
# Default paths, default blocks (Social media + Reputation)
python3 clean_socials.py

# Custom input/output and additional block (“Individuals”)
python3 clean_socials.py \
    --in  output/result.txt \
    --out output/clean_socials.json \
    --keep "Social media,Reputation,Individuals"
"""
import argparse
import json
import pathlib
import sys

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract URL blocks from PhoneInfoga text output."
    )
    p.add_argument(
        "--in", "-i",
        dest="infile",
        default="output/result.json",   # PhoneInfoga raw output (text)
        help="input PhoneInfoga result file (text, *not* JSON)",
    )
    p.add_argument(
        "--out", "-o",
        dest="outfile",
        default="output/clean_socials.json",
        help="destination JSON file",
    )
    p.add_argument(
        "--keep", "-k",
        default="Social media,Reputation",
        help="comma-separated list of section names to keep",
    )
    return p.parse_args()

def main() -> None:
    args = parse_args()

    infile  = pathlib.Path(args.infile).expanduser()
    outfile = pathlib.Path(args.outfile).expanduser()
    wanted_blocks = {b.strip() for b in args.keep.split(",") if b.strip()}

    if not infile.is_file():
        sys.exit(f"❌  Input file not found: {infile}")

    current = None
    rows = []

    with infile.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()

            # “Results for foo” → reset sub-block context
            if line.startswith("Results for"):
                current = None
                continue

            # “Social media:” / “Reputation:” / “Individuals:” …
            if line.endswith(":"):
                current = line.rstrip(":")
                continue

            # Collect URLs inside desired blocks
            if current in wanted_blocks and line.startswith("URL:"):
                url = line.partition("URL:")[2].strip()
                rows.append({"category": current, "url": url})

    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    print(f"✅  Extracted {len(rows)} URLs → {outfile}")

if __name__ == "__main__":
    main()

