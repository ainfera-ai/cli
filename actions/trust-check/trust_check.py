"""Trust-check script for the Ainfera GitHub Action.

Fetches the current trust score, then posts to /v1/github/trust-check with the
commit SHA to get a before/after diff. Emits a JSON blob to stdout containing
the markdown PR comment, the raw scores, and a pass/fail flag.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import httpx

DIMENSIONS = ("safety", "reliability", "quality", "performance", "reputation")


def _client() -> httpx.Client:
    api_url = os.environ.get("AINFERA_API_URL", "https://api.ainfera.ai").rstrip("/")
    api_key = os.environ["AINFERA_API_KEY"]
    return httpx.Client(
        base_url=api_url,
        headers={
            "X-Ainfera-Key": api_key,
            "User-Agent": "ainfera-action-trust-check",
        },
        timeout=30.0,
    )


def _extract_score(payload: dict[str, Any]) -> dict[str, Any]:
    score = payload.get("score") or payload.get("overall_score") or 0
    grade = payload.get("grade") or ""
    raw_dims = payload.get("dimensions") or {}
    if not raw_dims:
        raw_dims = {
            d: payload[f"{d}_score"]
            for d in DIMENSIONS
            if isinstance(payload.get(f"{d}_score"), (int, float))
        }
    return {"score": int(score) if score else 0, "grade": grade, "dimensions": raw_dims}


def _render_comment(
    *, before: dict[str, Any], after: dict[str, Any], threshold: int, failed: bool
) -> str:
    lines = ["## Ainfera Trust Check", ""]
    lines.append("| Dimension | Before | After | Change |")
    lines.append("|-----------|--------|-------|--------|")
    b_dims = before.get("dimensions") or {}
    a_dims = after.get("dimensions") or {}
    keys = list(a_dims.keys()) or list(b_dims.keys()) or list(DIMENSIONS)
    for key in keys:
        b = b_dims.get(key)
        a = a_dims.get(key)
        b_str = f"{float(b):.2f}" if isinstance(b, (int, float)) else "—"
        a_str = f"{float(a):.2f}" if isinstance(a, (int, float)) else "—"
        if isinstance(b, (int, float)) and isinstance(a, (int, float)):
            delta = float(a) - float(b)
            marker = " ⚠️" if delta <= -0.05 else ""
            change = f"{delta:+.2f}{marker}"
        else:
            change = "—"
        lines.append(f"| {key.capitalize()} | {b_str} | {a_str} | {change} |")

    lines.append("")
    b_score = before.get("score") or 0
    a_score = after.get("score") or 0
    score_delta = a_score - b_score
    lines.append(
        f"**Score: {before.get('grade', '?')} {b_score} → "
        f"{after.get('grade', '?')} {a_score} ({score_delta:+d})**"
    )
    if threshold > 0:
        status = "❌ FAILED" if failed else "✅ PASSED"
        lines.append(f"Status: {status} (threshold: {threshold})")
    return "\n".join(lines)


def main() -> int:
    agent_id = os.environ["AINFERA_AGENT_ID"]
    threshold = int(os.environ.get("AINFERA_THRESHOLD") or 0)
    commit_sha = os.environ.get("GITHUB_SHA", "")

    with _client() as http:
        # Current (after) score
        after_resp = http.get(f"/v1/trust/{agent_id}")
        after_resp.raise_for_status()
        after = _extract_score(after_resp.json())

        # Diff — may not be implemented on all API versions
        before = {"score": after["score"], "grade": after["grade"], "dimensions": after["dimensions"]}
        try:
            diff_resp = http.post(
                "/v1/github/trust-check",
                json={"agent_id": agent_id, "commit_sha": commit_sha},
            )
            if diff_resp.status_code < 400:
                body = diff_resp.json()
                if isinstance(body.get("before"), dict):
                    before = _extract_score(body["before"])
                if isinstance(body.get("after"), dict):
                    after = _extract_score(body["after"])
        except httpx.HTTPError:
            pass

    failed = threshold > 0 and (after["score"] or 0) < threshold
    comment = _render_comment(
        before=before, after=after, threshold=threshold, failed=failed
    )
    result = {
        "before": before,
        "after": after,
        "delta": (after.get("score") or 0) - (before.get("score") or 0),
        "threshold": threshold,
        "failed": failed,
        "comment": comment,
    }
    json.dump(result, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
