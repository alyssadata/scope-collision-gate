# Director Proof | Scope Collision Gate

This repo demonstrates a GitHub-native coordination gate that detects scope overlap across open Issues and PRs, and can warn or block merges.

## Proof in 3 clicks

### Click 1: Create two Issues with the same scope
1) Create **Issue A** using the “Coordination Work Item” template.
2) In the issue body, set:
   - `SCOPE: demo-scope`
   - `INTENT: Issue A (User A)`
3) Create **Issue B** using the same template.
4) In the issue body, set:
   - `SCOPE: demo-scope`
   - `INTENT: Issue B (User B)`

Expected:
- A collision notice is created (comment) indicating another open item already has `SCOPE: demo-scope`.

### Click 2: Open a PR with the colliding scope
1) From Issue A, create a branch (or create a branch from `main`).
2) On that branch, add a small file (example: `demo_a.md`) containing:
   - `SCOPE: demo-scope`
   - `INTENT: PR A demo`
3) Open **PR A** and include `SCOPE: demo-scope` in the PR description.

Expected (warn mode):
- The workflow posts a collision comment and the check still passes.

Expected (block mode):
- The workflow posts a collision comment and the check fails, preventing merge when required checks are enabled.

### Click 3: Verify evidence in GitHub Actions logs
1) Open PR A.
2) Go to **Checks**.
3) Open the run for **Coordination | Scope Collision Check**.

Expected:
- Log output shows `COORD_MODE` and a collision message.
- In block mode, the job exits non-zero when a collision is found.

## Modes
- `COORD_MODE=warn`: comment only (non-blocking)
- `COORD_MODE=block`: fails the check on collision (merge gate when required checks are enabled)

## What this proves
- Multiple contributors can declare the same `SCOPE`.
- The system detects overlap automatically using GitHub-native artifacts.
- In block mode, merges are prevented until scope is resolved.
- All outcomes are auditable via PR comments and Actions logs.

