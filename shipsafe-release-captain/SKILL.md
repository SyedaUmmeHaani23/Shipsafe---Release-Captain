---
name: shipsafe-release-decision-agent
description: A release DECISION agent, not a code reviewer - starts after development is finished and reads real commits since the last tag (including messy, non-conventional ones), runs tests in a sandbox and explains any failure's likely cause, classifies changes with its own judgment (using a keyword script only as rough triage), interprets external release-blast-radius in context, drafts release notes, and pauses for human approval before tagging or publishing. Use whenever asked to "prepare a release", "cut a release", "ship a new version", or similar for a given repository.
---

# ShipSafe — Release Decision Agent

## Why this is an agent, not a script — and not a code reviewer either
Tools like semantic-release already read commits, bump a version, and
publish — automatically, with no human step, and only if every commit
follows a strict tagging convention. That's a solved problem and this skill
does not try to be better at it.

Tools like CodeRabbit review pull requests as they're written — line-level
code quality, security findings, an internal component-dependency graph for
a single diff (their "Blast Radius" / "Architecture Impact"), and automatic
per-PR changelog entries. That is a real, different, upstream job: "what's
wrong with this change." This skill starts after that is already done. Its
question is: "given everything that changed since the last release, is the
release candidate ready to ship, what version should it be, and should I
proceed to the irreversible publish action."

What this skill adds on top of both of those:
- reading real, messy, inconsistent commit messages and diffs and still
  making the right call — no enforced convention required
- explaining WHY a test failure happened, not just that it happened
- interpreting what EXTERNAL release impact (registry downloads / known
  dependents) means for this specific change, not just reporting a number —
  a different lens from an internal code-dependency graph
- a genuine human approval gate before anything irreversible happens, ending
  in an actual tag + publish

Every step below should make one of those four things visible.

## When to use this skill
Whenever asked to prepare, cut, or ship a release for a specific GitHub
repository.

## Step-by-step workflow

1. **Find the last tag.** Use the GitHub tool. If there is no tag yet, use
   the first commit as the starting point and say so.

2. **List commits since that tag.** Pull messages, authors, and diffs where
   available.

3. **Clone and test in the sandbox.** Run the repo's real test command
   (check `package.json`, or the language's usual convention). Capture the
   actual output.

4. **Gate on test results, with a real explanation.**
   - Any failure -> stop. Identify which commit most likely caused it and
     explain why in plain language, then stop completely — no notes, no
     versioning, no approval step. This refusal-with-reasoning IS the
     deliverable for this path.
   - All pass -> continue.

5. **Classify commits — script first, your judgment second.** Run
   `scripts/classify.py` on the commit list as a rough mechanical triage
   pass (it only matches keyword patterns). Then personally review every
   commit's real message and diff, especially ones the script marked
   "other" or low-confidence, or ones with unconventional phrasing. Where
   your read differs from the script's, say so explicitly and explain why.
   Your final semver-bump proposal is your judgment, informed by but not
   bound to the script.

6. **Check external release impact, then interpret it.** Run
   `scripts/blast_radius.py <package_name> <registry>` for a raw external
   signal (registry downloads / known dependents). This is deliberately an
   OUTSIDE-the-repo signal — how many real consumers this release reaches —
   not an internal code-dependency graph. Then say what that number means
   for THIS release given what actually changed — low risk despite a big
   number if the change is internal-only; high risk even on a small number
   if it touches a widely-used public function.

7. **Draft release notes.** Breaking Changes / Features / Fixes, plain
   language, referencing real commits.

8. **Present and pause for approval.** Show: proposed version + reasoning
   (including any script overrides), interpreted blast-radius line, release
   notes. Ask explicitly: "Approve publishing v<X.Y.Z>? (yes/no)." Do not
   tag or publish without an explicit yes.

## Files in this skill
- `scripts/classify.py` — rough keyword-based triage only, not authoritative
- `scripts/blast_radius.py` — raw registry download-count lookup only, not
  a risk assessment on its own

## Guardrails
- Never fabricate test results, commit data, or download numbers.
- Never tag, push a tag, or publish without an explicit human "yes" after
  step 8.
- Never print or log API keys/tokens.
