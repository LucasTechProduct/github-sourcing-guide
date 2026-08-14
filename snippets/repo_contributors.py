#!/usr/bin/env python3
"""
repo_contributors.py - List the contributors of one or more GitHub repositories.

This is the core of the "start from repositories" method: the people who
actually ship code to a canonical project know the technology, a stronger
signal than a bio keyword.

Prints one login per line (deduplicated across repos), so you can pipe it
into enrich_profiles.py.

Usage:
  export GITHUB_TOKEN=your_token_here
  python repo_contributors.py fastify/fastify nestjs/nest > logins.txt
  python repo_contributors.py --top 30 django/django

Note on limits: the GitHub API paginates contributors and is rate limited.
For a maintained index across dozens of technologies, ranked by real activity,
see StarHunt: https://www.getstarhunt.com/github-sourcing.html
"""
import argparse
import os
import sys
import time

import requests

API = "https://api.github.com"


def _headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("[error] set GITHUB_TOKEN (https://github.com/settings/tokens, read-only is enough)",
              file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}


def _get(url, headers, params=None):
    """GET with basic rate-limit handling. Returns the response."""
    while True:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers.get("X-RateLimit-Reset", "0"))
            wait = max(reset - int(time.time()), 1)
            print(f"[rate limit] waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
            continue
        return r


def contributors(repo, headers, top=None):
    """Yield contributor logins for owner/repo, most active first."""
    logins, page = [], 1
    while True:
        r = _get(f"{API}/repos/{repo}/contributors", headers,
                 {"per_page": 100, "page": page, "anon": "false"})
        if r.status_code == 404:
            print(f"[warn] {repo} not found or has no contributors", file=sys.stderr)
            break
        r.raise_for_status()
        chunk = r.json()
        if not chunk:
            break
        for c in chunk:
            login = c.get("login")
            if login:
                logins.append(login)
        if top and len(logins) >= top:
            logins = logins[:top]
            break
        if len(chunk) < 100:
            break
        page += 1
    return logins


def main():
    ap = argparse.ArgumentParser(description="List contributors of GitHub repositories.")
    ap.add_argument("repos", nargs="+", help="one or more owner/repo, e.g. fastify/fastify")
    ap.add_argument("--top", type=int, default=None, help="keep only the top N contributors per repo")
    args = ap.parse_args()

    headers = _headers()
    seen = set()
    for repo in args.repos:
        for login in contributors(repo, headers, args.top):
            if login not in seen:
                seen.add(login)
                print(login)
    print(f"[done] {len(seen)} unique contributors across {len(args.repos)} repo(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
