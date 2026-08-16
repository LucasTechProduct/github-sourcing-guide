# How to source developers on GitHub, a free DIY guide

A practical, open-source guide to finding and recruiting developers on GitHub using only GitHub's own search and public API. No paid tools required.

I put this together while building [StarHunt](https://www.getstarhunt.com), because the manual method is worth knowing before you reach for any tool. It works, it is free, and it is a good way to learn how technical sourcing actually works. It also runs into real limits, covered at the end, which is where automating it starts to pay off.

## Contents

- [Why source on GitHub](#why-source-on-github)
- [Method 1: GitHub user search](#method-1-github-user-search)
- [Method 2: start from repositories (the strong signal)](#method-2-start-from-repositories-the-strong-signal)
- [Ready-made snippets](#ready-made-snippets)
- [Reference repositories to start from](#reference-repositories-to-start-from)
- [The limits of the DIY method](#the-limits-of-the-diy-method)
- [Contributing](#contributing)

## Why source on GitHub

GitHub is the richest public record of what an engineer actually builds. For hiring, that means you can evaluate candidates on evidence (their code, their contributions, the projects they ship) instead of on a resume or a LinkedIn headline.

The hard part is doing it at scale, because GitHub's search is built for code, not for people.

## Method 1: GitHub user search

GitHub lets you search users with qualifiers. Combine them in the search box at [github.com/search?type=users](https://github.com/search?type=users) or via the API.

### Cheat sheet

| Goal | Query |
| --- | --- |
| By main language | `language:python` |
| By location | `location:"Paris"` |
| By follower count | `followers:>=100` |
| By number of public repos | `repos:>=10` |
| Word in bio, name or login | `fullstack in:bio` |
| Has a public email | `is:user` plus check the profile |
| Combine everything | `language:go location:"Berlin" followers:>=50` |

Full reference: [Searching users](https://docs.github.com/en/search-github/searching-on-github/searching-users).

More copy-paste queries by use case: see [queries.md](queries.md).

### What this is good at

Quick, hands-on lookups when you already know roughly who you want and you are comfortable with query operators.

### What it misses

It matches keywords in the profile. A developer who ships to a major project every week but writes "software engineer" in their bio is invisible to `language:` and bio searches. And it ranks by "best match", which is close to follower count, not by real activity.

## Method 2: start from repositories (the strong signal)

The better approach is to start from the repositories that define a technology, then look at who actually contributes to them. If someone is among the active contributors of a canonical project, they know the technology, a stronger signal than anything in a bio.

1. Pick the reference repositories for your stack (see [reference-repos.md](reference-repos.md) for a starter list).
2. Pull their contributors.
3. Enrich each contributor's public profile.
4. Filter by location, activity, and whatever else matters.

The snippets below do exactly this.

## Ready-made snippets

Small, dependency-light Python scripts. They use the GitHub API and a personal access token (read-only is enough).

```bash
export GITHUB_TOKEN=your_token_here     # https://github.com/settings/tokens, read-only scope is enough
pip install -r requirements.txt
```

| Script | What it does |
| --- | --- |
| [`snippets/search_users.py`](snippets/search_users.py) | Search users by language, location, followers, then export to CSV |
| [`snippets/repo_contributors.py`](snippets/repo_contributors.py) | List the top contributors of one or more repositories |
| [`snippets/enrich_profiles.py`](snippets/enrich_profiles.py) | Turn a list of logins into a CSV of public profile data |

Example, find contributors to a few Node.js projects and export their profiles:

```bash
python snippets/repo_contributors.py fastify/fastify nestjs/nest prisma/prisma > logins.txt
python snippets/enrich_profiles.py --input logins.txt --location France --csv candidates.csv
```

## Reference repositories to start from

A short, hand-picked starter list of canonical repositories per technology lives in [reference-repos.md](reference-repos.md). It is deliberately a starting point, not an exhaustive index. Build your own list for the exact stack you hire for.

## The limits of the DIY method

It is worth being honest about where this stops working. GitHub Search returns at most 1000 results per query, no matter how many people actually match, so any broad search silently truncates. It is keyword-only, so it finds people who describe themselves the right way rather than everyone who does the work, and it orders results by "best match" instead of by recent contributions or the languages in someone's own repositories. Enriching profiles is one API call each, so a few hundred candidates means babysitting rate limits. Locations are free text ("Paris", "Paris, France", "IDF"), the same person turns up across several repos, and you dedupe and clean all of that by hand. Finding people is only half of it, organizing and exporting a shortlist is the other half.

At some point cleaning this up by hand costs more than it saves. That is the part I ended up automating in [StarHunt](https://www.getstarhunt.com/github-sourcing.html): it takes a plain-English brief or a job post, ranks people by their real GitHub activity, normalizes locations to metro areas, and exports a clean shortlist. There is a free tier if you want to hold it against your own scripts.

## Contributing

Better queries, new snippets, or additions to the reference list are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE). Use it, fork it, build on it.
