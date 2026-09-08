# Repository brain schema

## Directory contract

```text
brain/
├── .project-brain.json
├── README.md
├── index.md
├── log.md
├── architecture/
│   └── architecture-idx.md
├── decisions/
│   └── decisions-idx.md
├── techniques/
│   └── techniques-idx.md
├── conventions/
│   └── conventions-idx.md
├── raw/
└── dev-logs/
```

- `raw/` contains immutable user-approved source copies or provenance pointers.
- `architecture/` documents current implemented structure and flows.
- `decisions/` records decisions and rationale; supersede rather than erase history.
- `techniques/` stores reusable project-specific approaches.
- `conventions/` stores project rules that are actually adopted.
- `dev-logs/` stores substantial feature requirements, specifications, and reviews.
- `index.md` routes retrieval; it must not become a second copy of every page.
- `log.md` is append-only history, not current state.

## Knowledge page frontmatter

Every knowledge page except infrastructure files and category indexes uses:

```yaml
---
title: Human-readable title
abstract: One sentence used by indexes
status: draft | active | superseded | archived
date: YYYY-MM-DD
tags: [tag-one, tag-two]
sources:
  - path/to/source-or-URL
---
```

`sources` may be empty only for an explicitly marked proposal or convention created by the user. Prefer repository-relative paths and stable URLs. Never place secrets or private tokens in frontmatter.

## Index format

`brain/index.md` lists categories and their indexes:

```markdown
## Architecture
> Current modules, boundaries, and runtime flows.
- [[overview]] — One-line abstract.
```

Category indexes contain one entry per knowledge page:

```markdown
- [[page-name]] — Abstract text. `#tag-one` `#tag-two`
```

Use unique kebab-case filenames so wiki links resolve without directory-qualified names. Do not create a link until its target exists.

## Log format

Append entries in this form:

```markdown
## YYYY-MM-DD | operation | subject
- Summary of durable changes.
- Sources or revision: `abc1234`
- Related: [[page-name]]
```

Do not use the log as the only record of current architecture or decisions.

## Provenance and freshness

- Prefer exact file paths, symbol names, commands, commits, upstream URLs, and observed dates.
- Label inferred rationale as `Inference:`.
- When a source conflicts with code, record both and identify the governing authority.
- When external facts may change, record the verification date.
- Keep secrets, credentials, personal data, and proprietary documents out of the brain unless the user explicitly authorizes their storage and repository visibility is appropriate.

