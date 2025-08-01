#!/usr/bin/env python3
"""
run_onionrepo.py  —  Unified scraper for OnionRepo (clearnet or .onion)

Usage:
  python3 run_onionrepo.py <email|phone|username>        # auto, tries clearnet then Tor
  python3 run_onionrepo.py --tor <query>                 # force Tor / .onion
  python3 run_onionrepo.py --clearnet <query>            # force clearnet

Output:
  Saves JSON to output/onionrepo_result.json and prints a summary.
"""

import argparse, json, os, sys, time
import requests
from bs4 import BeautifulSoup

# ─── CONFIG ──────────────────────────────────────────────────────────────────────
CLEARNET_URL = "https://onionrepo.com/search"
ONION_URL    = "http://onionrepoabc123def.onion/search"   # ← REPLACE with mirror you found
TOR_PROXY    = "socks5h://127.0.0.1:9050"
HEADERS      = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
TIMEOUT      = 25  # seconds
# ────────────────────────────────────────────────────────────────────────────────

def make_session(use_tor: bool) -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    if use_tor:
        s.proxies.update({"http": TOR_PROXY, "https": TOR_PROXY})
    return s

def fetch_html(query: str, use_tor: bool) -> str | None:
    url = ONION_URL if use_tor else CLEARNET_URL
    session = make_session(use_tor)
    try:
        resp = session.post(url, data={"search": query}, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[!] {('Tor' if use_tor else 'Clearnet')} request failed → {e}")
        return None

def parse_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return []
    rows = table.find_all("tr")[1:]  # skip header row
    results = []
    for r in rows:
        cols = [c.text.strip() for c in r.find_all("td")]
        if len(cols) < 5:
            continue
        results.append({
            "filename": cols[0],
            "email":    cols[1],
            "password": cols[2],
            "hash":     cols[3],
            "source":   cols[4]
        })
    return results

def save_json(data: list):
    os.makedirs("output", exist_ok=True)
    path = "output/onionrepo_result.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Results saved → {path}")

def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--tor", action="store_true", help="Force Tor / .onion mirror")
    mode.add_argument("--clearnet", action="store_true", help="Force clearnet")
    ap.add_argument("query", help="Email, phone or username to search")
    args = ap.parse_args()

    # Decide routing mode
    if args.tor:
        routes = [True]
    elif args.clearnet:
        routes = [False]
    else:
        routes = [False, True]  # try clearnet first, then tor

    for use_tor in routes:
        route_name = "Tor/.onion" if use_tor else "clearnet"
        print(f"[*] Searching via {route_name} …")
        html = fetch_html(args.query, use_tor)
        if not html:
            continue
        data = parse_html(html)
        if data:
            print(f"[+] {len(data)} hits found via {route_name}")
            save_json(data)
            break
        else:
            print(f"[!] No hits via {route_name}")
    else:
        print("[×] Finished: no data found on any route.")

if __name__ == "__main__":
    main()

