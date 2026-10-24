"""TITANIUS autonomous hierarchy: bounded, self-hosted (GitHub Actions) evidence workers.

This is a real scheduled, standard-library execution loop, not consciousness.
No model/ChatGPT subscription is required to perform the deterministic work.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCHEMA = "titanius.control_center.v1"
ISSUE_TITLE = "[TITANIUS] Autonomous commercial control room"
STATE_MARK = "TITANIUS_CONTROL_STATE_V1:"
MAX_PAGE = 192_000
MAX_HISTORY = 16
ALLOWED_HOSTS = frozenset({
    "microvault.floot.app",
    "charlysmoky2010-hub.github.io",
    "ebru-alaca-storefront.vercel.app",
})
RUBRIC = (
    ("title", r"<title\b[^>]*>\s*\S"),
    ("description", r"<meta\b[^>]*name=['\"]description['\"]"),
    ("viewport", r"<meta\b[^>]*name=['\"]viewport['\"]"),
    ("h1", r"<h1\b"),
    ("canonical", r"<link\b[^>]*rel=['\"]canonical['\"]"),
    ("social_preview", r"<meta\b[^>]*property=['\"]og:title['\"]"),
    ("structured_data", r"application/ld\+json"),
    ("language", r"<html\b[^>]*lang=['\"][a-z]"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_url(url: str) -> str:
    obj = urllib.parse.urlsplit(url)
    if (obj.scheme != "https" or obj.hostname not in ALLOWED_HOSTS
        or obj.username or obj.password or obj.port not in (None, 443)
        or obj.query or obj.fragment):
        raise ValueError("Disallowed external website endpoint")
    return url


class DenyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch_public_site(url: str) -> dict[str, Any]:
    safe_url(url)
    opener = urllib.request.build_opener(DenyRedirect)
    request = urllib.request.Request(url, headers={
        "User-Agent": "TITANIUS-ReadOnly-Website-QA/1.0",
        "Accept": "text/html",
    })
    start = time.monotonic()
    try:
        with opener.open(request, timeout=12) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type:
                return {"status": response.status, "ok": False, "reason": "not_html", "html": ""}
            body = response.read(MAX_PAGE + 1)
            if len(body) > MAX_PAGE:
                return {"status": response.status, "ok": False, "reason": "html_over_limit", "html": ""}
            return {"status": response.status, "ok": response.status == 200,
                    "reason": None, "html": body.decode("utf-8", errors="replace"),
                    "latency_ms": int((time.monotonic() - start) * 1000)}
    except urllib.error.HTTPError as exc:
        # 3xx without redirect following is an observation, not a healthy page.
        return {"status": exc.code, "ok": False,
                "reason": "http_status", "html": ""}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"status": None, "ok": False,
                "reason": type(exc).__name__, "html": ""}


def load_config(path: str | Path) -> dict[str, Any]:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    if cfg.get("schema") != SCHEMA or cfg.get("brain") != "TITANIUS_CERBERRUS":
        raise ValueError("Not a TITANIUS v1 config")
    sites = cfg.get("sites")
    if not isinstance(sites, list) or not sites:
        raise ValueError("No targets")
    seen: set[str] = set()
    for site in sites:
        if site["id"] in seen or not re.fullmatch(r"[a-z0-9_]{3,50}", site["id"]):
            raise ValueError("Invalid/duplicate target")
        seen.add(site["id"])
        safe_url(site["url"])
        if not isinstance(site.get("required"), list):
            raise ValueError("Missing expected offer markers")
    agents = cfg.get("agents", [])
    names = {a["id"] for a in agents}
    if len(names) != len(agents) or len(names) < 7:
        raise ValueError("Expected distinct specialist brains")
    if cfg["policy"].get("payment_mutations") is not False or cfg["policy"].get("external_messages") is not False:
        raise ValueError("Unsafe delegated action policy")
    return cfg


def audit_site(site: dict[str, Any], fetch: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    result = fetch(site["url"])
    info = {k: result.get(k) for k in ("status", "ok", "reason", "latency_ms")}
    info["site_id"] = site["id"]
    info["owner"] = site["owner"]
    # Rubric measures only *checkable on-page signals*, never human design taste.
    if not result.get("ok"):
        info.update({"marker_results": {}, "rubric": {}, "score": None})
        return info
    markup = result.get("html", "")
    info["rubric"] = {
        key: bool(re.search(pattern, markup, flags=re.IGNORECASE | re.DOTALL))
        for key, pattern in RUBRIC
    }
    info["score"] = int(round(sum(info["rubric"].values()) / len(RUBRIC) * 100))
    info["marker_results"] = {
        marker: html.unescape(marker).casefold() in html.unescape(markup).casefold()
        for marker in site.get("required", [])
    }
    # The private HTML body stays in this job's memory and never enters issues.
    return info


def task_id(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def task(key: str, agent: str, priority: int, title: str, proof: str,
         action: str, permission: str = "review") -> dict[str, Any]:
    return {"id": task_id(key), "agent": agent, "priority": priority,
            "title": title, "evidence": proof, "next_action": action,
            "permission": permission}


def run_cycle(config: dict[str, Any], fetch: Callable[[str], dict[str, Any]],
              previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous if isinstance(previous, dict) and previous.get("schema") == "titanius.cycle.v1" else {}
    sites = [audit_site(site, fetch) for site in config["sites"]]
    pending = []
    for result in sites:
        name = result["site_id"]
        if not result["ok"]:
            pending.append(task(name + ":offline", "operations_brain", 100,
                name + " public website is not confirmed available",
                "HTTP=" + str(result["status"]) + "; reason=" + str(result["reason"]),
                "Inspect DNS, deployment and HTTP response (no automatic publish)."))
            continue
        for marker, ok in result["marker_results"].items():
            if not ok:
                pending.append(task(name + ":marker:" + marker, "commerce_brain", 85,
                    name + " required offer information not visible",
                    "Missing expected public marker: " + marker,
                    "Review product-page content; change only after evidence and approval."))
        missing = [k for k, v in result["rubric"].items() if not v]
        if missing:
            pending.append(task(name + ":design", "design_brain", 55,
                name + " measurable page metadata is incomplete",
                "Missing: " + ", ".join(missing),
                "Prepare accessible, source-backed SEO/AEO/design changes for review."))
    # Real provider data is unavailable to this runner; NEVER infer receipts
    # or delivery from payment links, traffic, sample CSVs, or hosted HTML.
    pending.append(task("provider_payment_evidence", "finance_intelligence", 95,
        "Verified net revenue cannot yet be independently reconciled",
        "No authenticated, read-only Stripe reconciliation configured for this Action",
        "Integrate signed read-only payment status, refunds and payouts before claiming income."))
    pending.append(task("delivery_receipt_proof", "delivery_brain", 88,
        "A paid customer's completed report download remains unverified",
        "No real paid Stripe session + completed entitlement + download receipt provided",
        "Require one real receipt-backed fulfillment event; never create a fake buyer."))
    pending.sort(key=lambda t: (-t["priority"], t["id"]))

    last_tasks = {t["id"]: t for t in previous.get("tasks", []) if isinstance(t, dict) and "id" in t}
    for entry in pending:
        former = last_tasks.get(entry["id"])
        entry["seen_cycles"] = min(10000, int(former.get("seen_cycles", 0)) + 1) if former else 1
        entry["status"] = "blocked" if entry["permission"] == "review" else "open"
    previously_open = set(last_tasks)
    resolved = sorted(previously_open.difference(t["id"] for t in pending))
    snapshot = {s["site_id"]: {"ok": s["ok"], "status": s["status"], "score": s["score"]}
                for s in sites}
    prior_snapshot = previous.get("snapshot", {})
    changes = [{"site": key, "before": prior_snapshot.get(key), "after": value}
               for key, value in snapshot.items()
               if key in prior_snapshot and prior_snapshot[key] != value]
    history = [str(v) for v in previous.get("history", [])][-MAX_HISTORY + 1:]
    history.append(utc_now())
    return {
        "schema": "titanius.cycle.v1", "brain": "TITANIUS_CERBERRUS",
        "checked_at": utc_now(), "agents": [a["id"] for a in config["agents"]],
        "snapshot": snapshot, "sites": sites, "tasks": pending[:25],
        "resolved_since_previous": resolved[:25], "changes": changes,
        "history": history, "cycles_observed": min(10000, int(previous.get("cycles_observed", 0)) + 1),
        "finance": {"verified_net_revenue_eur": None, "confirmed_paid_orders": None,
                    "confirmed_deliveries": None, "status": "not_connected_to_authoritative_payments"},
        "activity": {"public_web_checks": len(sites), "external_payments": 0,
                     "customer_messages": 0, "automatic_publishing": 0,
                     "ai_model_used": False},
        "autonomy": "GitHub scheduled read-only workers with persistent issue queue; no self-directed LLM",
    }


def issue_markdown(report: dict[str, Any]) -> str:
    lines = [
        "## TITANIUS · Autonomous Commercial Control Room",
        "",
        "Main brain: **TITANIUS_CERBERRUS** · Next action is selected from real public checks.",
        "Last scheduled cycle (UTC): **" + report["checked_at"] + "**",
        "Successful cycles reflected in this persistent issue: **" + str(report["cycles_observed"]) + "**",
        "",
        "### Live observations",
        "| Site | HTTP | Web rubric (not an aesthetic 10/10) | Required offer content |",
        "|---|---|---|---|",
    ]
    for site in report["sites"]:
        markers = site["marker_results"]
        lines.append("| " + site["site_id"] + " | " + str(site["status"]) +
            " | " + (str(site["score"]) + "/100" if site["score"] is not None else "unknown") +
            " | " + (str(sum(markers.values())) + "/" + str(len(markers)) if markers else "not evaluated") + " |")
    lines.extend(["", "### Active agent tasks", "| Priority | Agent | Status | Verified blocker / task |",
        "|---|---|---|---|"])
    for x in report["tasks"]:
        # Strings come solely from static config and fixed error categories;
        # sanitize delimiters to preserve the audit table.
        lines.append("| " + str(x["priority"]) + " | " + x["agent"] + " | " + x["status"] +
            " | " + x["title"].replace("|", "/") + " — " + x["evidence"].replace("|", "/") + " |")
    lines.extend(["", "### Truth / memory gate",
        "- Revenue and paid delivery: **UNKNOWN**, no read-only authoritative financial feed. No fictional sales.",
        "- A working checkout CTA is **not** evidence of payment or file delivery.",
        "- The website rubric scores observable metadata, **not** design taste, legal compliance or user conversions.",
        "- Changes from previous observation: " + str(len(report["changes"])) +
        "; resolved previously logged tasks: " + str(len(report["resolved_since_previous"])) + ".",
        "- Scheduler executes only configured read-only checks. Human review remains mandatory for deployment, legal, payouts and outreach.",
        "", "### Machine-readable persistent state", "",
    ])
    # No secrets, user input, payment session IDs, PII, or raw HTML.
    compact = {key: report[key] for key in ("schema", "checked_at", "cycles_observed", "snapshot",
               "tasks", "history", "finance")}
    lines.append("<!-- " + STATE_MARK + json.dumps(compact, separators=(",", ":"), ensure_ascii=True) + " -->")
    return "\n".join(lines)[:60000]


def github_api(method: str, path: str, token: str, data: Any = None) -> Any:
    root = "https://api.github.com"
    url = root + path
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "TITANIUS-Control-Center/1.0"}
    body = None if data is None else json.dumps(data).encode("utf-8")
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read(131072).decode("utf-8"))


def load_persisted_issue(token: str, repo: str) -> tuple[int | None, dict[str, Any]]:
    # The issue is an audit/state store, not a source of purchase truth.
    path = "/repos/" + repo + "/issues?state=open&per_page=100"
    for issue in github_api("GET", path, token):
        if issue.get("title") != ISSUE_TITLE or "pull_request" in issue:
            continue
        body = str(issue.get("body") or "")
        found = re.search(r"<!-- " + STATE_MARK + r"(\{.*?\}) -->", body, flags=re.DOTALL)
        try:
            state = json.loads(found.group(1)) if found else {}
            if state.get("schema") != "titanius.cycle.v1":
                state = {}
        except (ValueError, AttributeError):
            state = {}
        return issue["number"], state
    return None, {}


def persist_issue(token: str, repo: str, number: int | None, report: dict[str, Any]) -> dict[str, Any]:
    payload = {"title": ISSUE_TITLE, "body": issue_markdown(report)}
    if number is None:
        return github_api("POST", "/repos/" + repo + "/issues", token, payload)
    return github_api("PATCH", "/repos/" + repo + "/issues/" + str(number), token, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/titanius_control_center.v1.json")
    parser.add_argument("--output", default="runtime/control_center/latest.json")
    parser.add_argument("--publish-issue", action="store_true")
    args = parser.parse_args()
    cfg = load_config(args.config)
    issue_number = None
    prev: dict[str, Any] = {}
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if args.publish_issue:
        if not token or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise RuntimeError("GitHub issue state requires GITHUB_TOKEN and GITHUB_REPOSITORY")
        issue_number, prev = load_persisted_issue(token, repo)
    report = run_cycle(cfg, fetch_public_site, prev)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "measured", "agents": len(report["agents"]),
        "sites": len(report["sites"]), "open_tasks": len(report["tasks"]),
        "verified_revenue": "unknown", "issue_published": bool(args.publish_issue)}))
    if args.publish_issue:
        result = persist_issue(token, repo, issue_number, report)
        print("Persistent issue: " + str(result.get("html_url", "unknown")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
