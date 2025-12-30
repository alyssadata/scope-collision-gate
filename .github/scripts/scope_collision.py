import os
import re
import sys
import json
import urllib.request
from typing import Optional, Tuple, List, Dict

API = "https://api.github.com"


def gh_request(method: str, url: str, token: str, data: Optional[dict] = None) -> dict:
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "coordination-scope-collision")
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = body
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def get_event() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        print("Missing GITHUB_EVENT_PATH, cannot run in this environment.")
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


SCOPE_RE = re.compile(r"(?im)^\s*SCOPE\s*:\s*([a-z0-9._/\-]+)\s*$")


def extract_scope(text: str) -> Optional[str]:
    if not text:
        return None
    m = SCOPE_RE.search(text)
    return m.group(1).strip().lower() if m else None


def list_open_issues_and_prs(owner: str, repo: str, token: str) -> List[dict]:
    # Includes issues and PRs. PRs appear as issues with pull_request field.
    url = f"{API}/repos/{owner}/{repo}/issues?state=open&per_page=100"
    items = gh_request("GET", url, token)
    if not isinstance(items, list):
        return []
    return items


def post_issue_comment(owner: str, repo: str, token: str, issue_number: int, body: str) -> None:
    url = f"{API}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    gh_request("POST", url, token, {"body": body})


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Missing GITHUB_TOKEN")
        return 2

    mode = os.environ.get("COORD_MODE", "warn").strip().lower()
    if mode not in ("warn", "block"):
        mode = "warn"

    event = get_event()
    repo_full = event.get("repository", {}).get("full_name", "")
    if "/" not in repo_full:
        print("Cannot determine repository full_name from event payload.")
        return 2

    owner, repo = repo_full.split("/", 1)

    # Determine whether this is an issue or PR event
    issue = event.get("issue")
    pr = event.get("pull_request")

    if issue:
        number = issue.get("number")
        title = issue.get("title", "")
        body = issue.get("body", "") or ""
        item_type = "issue"
    elif pr:
        number = pr.get("number")
        title = pr.get("title", "")
        body = pr.get("body", "") or ""
        item_type = "pull_request"
    else:
        print("Unsupported event type. Expected issues or pull_request.")
        return 0

    if not number:
        print("Missing issue/PR number.")
        return 2

    scope = extract_scope(body)
    if not scope:
        # No scope means we do not block. We can optionally remind.
        return 0

    open_items = list_open_issues_and_prs(owner, repo, token)

    collisions: List[Tuple[int, str, str]] = []
    for it in open_items:
        it_number = it.get("number")
        if it_number == number:
            continue

        it_title = it.get("title", "")
        it_body = it.get("body", "") or ""
        it_scope = extract_scope(it_body)
        if not it_scope:
            continue

        if it_scope == scope:
            url = it.get("html_url", "")
            kind = "PR" if "pull_request" in it else "Issue"
            collisions.append((it_number, kind, url))

    if not collisions:
        return 0

    lines = []
    lines.append("## ⚠️ Scope collision detected")
    lines.append("")
    lines.append(f"**SCOPE:** `{scope}`")
    lines.append("")
    lines.append("This scope is already active in the following open items:")
    for n, kind, url in collisions:
        lines.append(f"- {kind} #{n}: {url}")
    lines.append("")
    lines.append("### Resolution options")
    lines.append("- Assign a primary owner and link the other item as dependent")
    lines.append("- Split scope into two non-overlapping scopes")
    lines.append("- Close one item if it is a duplicate")
    lines.append("")
    lines.append("Receipt: this comment is the collision notice. Add a decision record if you resolve by splitting or re-assigning ownership.")

    comment = "\n".join(lines)

    # Post comment on the triggering issue/PR (both are addressed via Issues API)
    post_issue_comment(owner, repo, token, int(number), comment)

    # For PRs, failing this check makes it gateable if required checks are enabled.
    if item_type == "pull_request" and mode == "block":
        print(f"Collision found for PR #{number}, failing because COORD_MODE=block.")
        return 1

    print(f"Collision found for {item_type} #{number}, mode={mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
