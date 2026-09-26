#!/usr/bin/env python3
"""
classify.py — ROUGH TRIAGE ONLY. Keyword/pattern matching on commit
messages and diffs. This script cannot understand meaning, tone, or intent
— it only catches commits that happen to follow known conventions or
contain known phrases. It WILL miss or misjudge messy, real-world commit
messages. The agent using this script must treat every "other" or
low-confidence result as "needs my own reading," not as a final answer.

Usage:
    python classify.py commits.json

commits.json is a list of objects like:
    [{"sha": "abc123", "message": "fix: handle empty input", "diff": "..."}]

Prints a JSON report: each commit's classification, a confidence label, and
the overall suggested semver bump — clearly marked as a first pass.
"""

import json
import re
import sys

BREAKING_KEYWORDS = [
    r"breaking change", r"breaking:",
    r"remove(d)? (public )?(function|method|endpoint|api|option|config)",
    r"rename(d)? (public )?(function|method|endpoint|api)",
    r"change(d)? (the )?(default|signature|behavior)",
    r"drop support",
    r"no longer support",
]

FEAT_PREFIXES = [r"^feat(\(.+\))?:", r"^feature(\(.+\))?:"]
FIX_PREFIXES = [r"^fix(\(.+\))?:", r"^bugfix(\(.+\))?:", r"^hotfix(\(.+\))?:"]

BREAKING_RE = re.compile("|".join(BREAKING_KEYWORDS), re.IGNORECASE)
FEAT_RE = re.compile("|".join(FEAT_PREFIXES), re.IGNORECASE)
FIX_RE = re.compile("|".join(FIX_PREFIXES), re.IGNORECASE)

VAGUE_PATTERNS = [
    r"^cleanup", r"^update stuff", r"^misc", r"^wip", r"^small changes?$",
    r"^tweaks?$", r"^stuff$",
]
VAGUE_RE = re.compile("|".join(VAGUE_PATTERNS), re.IGNORECASE)


def classify_commit(commit):
    message = commit.get("message", "")
    diff = commit.get("diff", "") or ""
    first_line = message.splitlines()[0] if message else ""
    haystack = f"{message}\n{diff}"

    has_conventional_marker = bool(re.match(r"^\w+(\(.+\))?!?:", first_line))
    is_vague = bool(VAGUE_RE.search(first_line))

    if re.search(r"^\w+(\(.+\))?!:", first_line):
        return {
            "sha": commit.get("sha"), "message": first_line[:120],
            "category": "breaking", "confidence": "high",
            "reason": "Conventional-commit '!' marker indicates a breaking change.",
        }
    if BREAKING_RE.search(haystack):
        return {
            "sha": commit.get("sha"), "message": first_line[:120],
            "category": "breaking", "confidence": "medium",
            "reason": "Matched a breaking-change keyword in the message or diff. "
                      "Agent should confirm this is really user-facing, not just phrased that way.",
        }
    if FEAT_RE.search(message):
        return {
            "sha": commit.get("sha"), "message": first_line[:120],
            "category": "feat", "confidence": "medium",
            "reason": "feat: prefix and no breaking-change keyword found — "
                      "agent should still check the diff for undeclared breaking changes.",
        }
    if FIX_RE.search(message):
        return {
            "sha": commit.get("sha"), "message": first_line[:120],
            "category": "fix", "confidence": "medium",
            "reason": "fix: prefix found — agent should confirm this doesn't also "
                      "remove/rename anything public (a mislabeled breaking change).",
        }
    if is_vague or not has_conventional_marker:
        return {
            "sha": commit.get("sha"), "message": first_line[:120],
            "category": "other", "confidence": "low",
            "reason": "No recognizable convention or a vague message — this script "
                      "cannot judge this commit. The agent MUST read the actual "
                      "message and diff itself before deciding.",
        }
    return {
        "sha": commit.get("sha"), "message": first_line[:120],
        "category": "other", "confidence": "low",
        "reason": "Did not match any known pattern — needs the agent's own reading.",
    }


def suggest_bump(classified):
    categories = {c["category"] for c in classified}
    low_conf_count = sum(1 for c in classified if c["confidence"] == "low")
    if "breaking" in categories:
        bump = "major"
    elif "feat" in categories:
        bump = "minor"
    elif "fix" in categories:
        bump = "patch"
    else:
        bump = "patch"
    return bump, low_conf_count


def main():
    if len(sys.argv) != 2:
        print("Usage: python classify.py commits.json", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        commits = json.load(f)

    classified = [classify_commit(c) for c in commits]
    bump, low_conf_count = suggest_bump(classified)

    report = {
        "commits": classified,
        "script_suggested_bump": bump,
        "low_confidence_commit_count": low_conf_count,
        "note": "THIS IS TRIAGE, NOT A VERDICT. The agent must personally review "
                "every 'low' confidence commit and every 'other' category before "
                "finalizing the version bump — that review is the actual job.",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
