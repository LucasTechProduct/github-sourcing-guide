#!/usr/bin/env python3
"""
enrich_profiles.py - Turn a list of GitHub logins into a CSV of public profile data.

Reads logins (one per line) from a file or stdin, fetches each public profile,
optionally filters by location, and writes a CSV.

Usage:
  export GITHUB_TOKEN=your_token_here
  python enrich_profiles.py --input logins.txt --csv candidates.csv
  python repo_contributors.py fastify/fastify | python enrich_profiles.py --location France --csv fr.csv

Only public data is fetched (the same fields anyone sees on github.com).
Enriching many profiles means one API call each, so mind the rate limit. This
by-hand cost is exactly what an automated index removes:
https://www.getstarhunt.com/github-sourcing.html
"""
import argparse
import csv
import os
import sys
import time

import requests

API = "https://api.github.com"
FIELDS = ["login", "name", "location", "company", "email", "blog",
          "followers", "public_repos", "hireable", "html_url"]


def _headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("[error] set GITHUB_TOKEN (read-only is enough)", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}


def _get(url, headers):
    while True:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers.get("X-RateLimit-Reset", "0"))
            wait = max(reset - int(time.time()), 1)
            print(f"[rate limit] waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r


def fetch_profile(login, headers):
    r = _get(f"{API}/users/{login}", headers)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    d = r.json()
    return {k: d.get(k) for k in FIELDS}


def read_logins(path):
    stream = open(path, encoding="utf-8") if path and path != "-" else sys.stdin
    for line in stream:
        login = line.strip()
        if login and not login.startswith("#"):
            yield login


def main():
    ap = argparse.ArgumentParser(description="Enrich GitHub logins into a CSV of public profiles.")
    ap.add_argument("--input", "-i", default="-", help="file of logins, or - for stdin (default)")
    ap.add_argument("--location", help="keep only profiles whose location contains this text (case-insensitive)")
    ap.add_argument("--csv", help="output CSV path (default: stdout)")
    args = ap.parse_args()

    headers = _headers()
    rows = []
    for login in read_logins(args.input):
        p = fetch_profile(login, headers)
        if not p:
            continue
        if args.location:
            loc = (p.get("location") or "").lower()
            if args.location.lower() not in loc:
                continue
        rows.append(p)
        print(f"[ok] {login}", file=sys.stderr)

    out = open(args.csv, "w", newline="", encoding="utf-8") if args.csv else sys.stdout
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    print(f"[done] {len(rows)} profiles written", file=sys.stderr)


if __name__ == "__main__":
    main()
