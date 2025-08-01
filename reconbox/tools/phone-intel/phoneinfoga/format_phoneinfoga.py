#!/usr/bin/env python3
"""
format_phoneinfoga.py
Read PhoneInfoga stdout from stdin and print only the useful URL blocks
in a neat, copy-friendly way.
"""
import sys, argparse, re
from collections import defaultdict

def parse(stream, keep):
    keep = {s.strip() for s in keep.split(",") if s.strip()}
    current = None
    buckets = defaultdict(list)
    url_re = re.compile(r'^URL:\s*(\S+)')

    for raw in stream:
        line = raw.strip()

        # reset when a new scanner section begins
        if line.startswith("Results for"):
            current = None
            continue

        # detect block headers like “Social media:”
        if line.endswith(":"):
            current = line[:-1]
            continue

        # collect URLs inside the chosen blocks
        m = url_re.match(line)
        if current and current in keep and m:
            buckets[current].append(m.group(1))

    # de-duplicate while preserving order
    for k, urls in buckets.items():
        seen, uniq = set(), []
        for u in urls:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        buckets[k] = uniq
    return buckets

def main():
    ap = argparse.ArgumentParser(
        description="Pretty-print PhoneInfoga links from stdin")
    ap.add_argument("--keep", default="Social media,Reputation,Individuals",
                    help="Comma-separated block names to keep "
                         "(default: Social media,Reputation,Individuals)")
    args = ap.parse_args()

    buckets = parse(sys.stdin, args.keep)
    total   = sum(len(v) for v in buckets.values())

    print(f"\n=== PhoneInfoga Links — {total} total "
          f"(kept: {', '.join(buckets) or 'none'}) ===\n")
    for cat in sorted(buckets):
        urls = buckets[cat]
        print(f"-- {cat} ({len(urls)}) --")
        for idx, url in enumerate(urls, 1):
            print(f"{idx:2d}) {url}")
        print()
    if total == 0:
        print("No links found. Try a different --keep list.\n")

if __name__ == "__main__":
    main()

