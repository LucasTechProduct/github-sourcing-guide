# Copy-paste GitHub search queries

Paste these into the search box at [github.com/search?type=users](https://github.com/search?type=users), or adapt the qualifiers. Swap the values for your own.

## By technology and location

| Use case | Query |
| --- | --- |
| Python developers in Paris | `language:python location:"Paris"` |
| Senior Go developers in Berlin | `language:go location:"Berlin" followers:>=100` |
| Rust developers, active accounts | `language:rust repos:>=10 followers:>=30` |
| React developers in the US | `language:javascript react in:bio location:"United States"` |
| Data engineers mentioning Spark | `spark in:bio language:scala` |

## By profile signal

| Use case | Query |
| --- | --- |
| Word in bio | `devops in:bio` |
| Word in name or login | `kubernetes in:login,name` |
| Many followers | `followers:>=500` |
| Prolific accounts | `repos:>=50` |
| Joined before a date | `created:<2018-01-01` |

## Notes

- Wrap multi-word values in quotes: `location:"San Francisco"`.
- Qualifiers combine with a space (logical AND).
- Location is free text on GitHub, so `location:"Paris"` misses `location:"Paris, France"` and suburbs. Search a few variants.
- GitHub Search returns at most 1000 results per query.

Full operator reference: https://docs.github.com/en/search-github/searching-on-github/searching-users
