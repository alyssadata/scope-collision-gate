# scope-collision-gate

GitHub-native coordination gate that detects scope overlap across open Issues and PRs. Supports warn-only mode or merge-blocking mode via required checks.

## Why This Matters

Coordination failures in software development occur when multiple contributors work on overlapping scope without awareness, leading to merge conflicts, duplicated effort, and integration problems. This gate provides automated boundary detection to prevent scope collisions before they reach the main branch.

This approach mirrors AI safety evaluation methodology: detect boundary violations early, maintain clear scope separation, and preserve audit trails. The same systematic thinking applies to preventing AI systems from absorbing conflicting instructions or merging user intent into core identity.

## Canonical format (do not change labels)
This gate parses literal labels from Issue bodies and PR descriptions:

    SCOPE: <scope-key>
    INTENT: <one-line why/what>

## What it does
- Scans open Issues and PRs for `SCOPE:`
- Flags collisions when the same scope appears in multiple open items
- Posts an evidence-linked collision notice
- In `block` mode, fails the PR check on collision (pre-merge gate)

## Install
Copy into your repo:
- `.github/workflows/coordination_scope_collision.yml`
- `.github/scripts/scope_collision.py`

(Optional but recommended)
- `.github/ISSUE_TEMPLATE/coordination_work_item.yml`

## Use
1) Create Issues using the issue template (it inserts the canonical labels).
2) Ensure PR descriptions include the canonical labels (at minimum `SCOPE:`).

## Modes (warn vs block)
Set `COORD_MODE` in the workflow:
- `warn`: comment only (non-blocking)
- `block`: comment + fail check on collision (merge gate when required checks are enabled)

## Docs
- docs/director_proof.md
- docs/design_notes.md

## Notes
- No auto-merge, no auto-approve
- Auditable via PR comments and GitHub Actions logs

Portfolio map: https://github.com/alyssadata/PORTFOLIO_MAP.md
