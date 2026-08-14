#!/usr/bin/env python3
"""
search_users.py - Find GitHub users by criteria via the GitHub Search API, then
export their public profiles to CSV.

This is the keyword-based method (Method 1). Reminder of its ceiling: GitHub
Search returns at most 1000 results per query and ranks by "best match", not by
real activity. For ranked, deduplicated results from a plain-English brief, see
StarHunt: https://www.getstarhunt.com/github-sourcing.html

Usage:
  export GITHUB_TOKEN=your_token_here
  python search_users.py --language python --location Paris --min-followers 50 --csv out.csv
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


def _get(url, headers, params=None):
    while True:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers.get("X-RateLimit-Reset", "0"))
            wait = max(reset - int(time.time()), 1)
            print(f"[rate limit] waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r


def build_query(args):
    parts = []
    if args.language:
        parts.append(f"language:{args.language}")
    if args.location:
        parts.append(f'location:"{args.location}"')
    if args.min_followers:
        parts.append(f"followers:>={args.min_followers}")
    if args.min_repos:
        parts.append(f"repos:>={args.min_repos}")
    for kw in args.keyword or []:
        parts.append(kw)
    return " ".join(parts)


def search_logins(query, headers, max_results):
    logins, page = [], 1
    while len(logins) < max_results:
        r = _get(f"{API}/search/users", headers,
                 {"q": query, "per_page": 100, "page": page})
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            break
        logins.extend(i["login"] for i in items)
        if page * 100 >= 1000:
            print("[note] reached GitHub Search's 1000-result ceiling", file=sys.stderr)
            break
        page += 1
    return logins[:max_results]


def fetch_profile(login, headers):
    r = _get(f"{API}/users/{login}", headers)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    d = r.json()
    return {k: d.get(k) for k in FIELDS}


def main():
    ap = argparse.ArgumentParser(description="Search GitHub users and export public profiles to CSV.")
    ap.add_argument("--language")
    ap.add_argument("--location")
    ap.add_argument("--min-followers", type=int, dest="min_followers")
    ap.add_argument("--min-repos", type=int, dest="min_repos")
    ap.add_argument("--keyword", action="append", help="extra qualifier or word, can repeat")
    ap.add_argument("--max", type=int, default=100, dest="max_results", help="max profiles (default 100)")
    ap.add_argument("--csv", help="output CSV path (default: stdout)")
    args = ap.parse_args()

    query = build_query(args)
    if not query:
        print("[error] give at least one criterion (--language, --location, ...)", file=sys.stderr)
        sys.exit(1)
    print(f"[query] {query}", file=sys.stderr)

    headers = _headers()
    logins = search_logins(query, headers, args.max_results)
    rows = []
    for login in logins:
        p = fetch_profile(login, headers)
        if p:
            rows.append(p)
            print(f"[ok] {login}", file=sys.stderr)

    out = open(args.csv, "w", newline="", encoding="utf-8") if args.csv else sys.stdout
    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    print(f"[done] {len(rows)} profiles written", file=sys.stderr)


if __name__ == "__main__":
    main()
