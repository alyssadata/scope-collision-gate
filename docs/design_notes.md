# Design Notes | Scope Collision Gate

## Purpose
Prevent duplicated work from landing in `main` when multiple contributors declare the same scope in parallel. The gate is GitHub-native and auditable.

## Core behavior
- Parse `SCOPE:` from open Issues and PRs (and optionally PR descriptions / files, depending on implementation).
- If two or more open items share the same scope, treat it as an active collision.
- Output must be evidence-linked: list the colliding items with identifiers (issue/PR numbers and URLs) and where the scope was found (body/description).

## Inputs (current assumptions)
- Issues: issue body contains literal lines:
  - `SCOPE: <value>`
  - `INTENT: <value>`
- PRs: PR description contains `SCOPE: <value>` and optionally `INTENT: <value>`.
- Mode is controlled by environment variable `COORD_MODE`:
  - `warn` (comment only)
  - `block` (fail check on collision)

## Outputs
### In warn mode
- Post a comment on the Issue/PR noting:
  - scope value
  - list of other open items with the same scope
  - a short resolution hint (close duplicate, change scope, or assign primary)

### In block mode
- Post the same collision comment
- Exit non-zero so the GitHub check fails

## Collision resolution patterns
A collision is resolved when:
- One of the colliding items is closed, OR
- One item changes scope to a unique value, OR
- A “primary owner” choice is recorded and the non-primary item is closed or re-scoped

Recommended human workflow:
1) Decide primary item for the scope
2) Close or re-scope the duplicate
3) Re-run checks on any blocked PR

## Safety / non-goals
- No auto-merge, no auto-approve
- No hidden memory across runs; all durable state is in GitHub artifacts (issues/PRs/comments)
- No sensitive content should be pasted into bot comments
- The gate should avoid strong claims without evidence (only report what is found in GitHub items)

## Failure modes and mitigations
- False positives from overly broad scopes:
  - Mitigation: encourage short, specific scope keys; add optional scope taxonomy later
- “Stale” open items causing collisions:
  - Mitigation: close stale issues; consider an age threshold or label-based filtering later
- Admin bypass:
  - Mitigation: require checks in branch protection; optionally restrict bypass in repo settings

## Roadmap (next useful increments)
- Config file (repo-local) for:
  - scope patterns / allowed prefixes
  - ignore labels (e.g., `coord-ignore`)
  - item types to scan (issues only, PRs only, both)
- “Owner of scope” convention (label or comment marker) to reduce churn
- Better parsing:
  - accept `SCOPE:` in PR body and/or changed files (optional)
- Resolution command keywords in comments (future):
  - e.g., `/coord resolve primary:#58 duplicate:#59`
- Summary output:
  - optional weekly digest of active scopes and owners

