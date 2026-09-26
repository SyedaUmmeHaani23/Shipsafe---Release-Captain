ShipSafe — Release Decision Agent

Why this is an agent, not a script — and not a code reviewer either

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

reading real, messy, inconsistent commit messages and diffs and still
making the right call — no enforced convention required

explaining WHY a test failure happened, not just that it happened

treating every commit message as a CLAIM rather than ground truth, and
building a pass/fail Release Contract from actual diff, test, and sandbox
EVIDENCE instead — surfacing the exact moment a claim and the evidence
disagree ("claim overridden by evidence")

interpreting what EXTERNAL release impact (registry downloads / known
dependents) means for this specific change, not just reporting a number —
a different lens from an internal code-dependency graph

a genuine human approval gate before anything irreversible happens, ending
in an actual tag + publish

Every step below should make one of those five things visible.

Design phrase

Trust nothing. Verify everything. This isn't a slogan bolted on afterward —
the Release Contract step below is what makes it literally true: nothing is
marked PASS without cited evidence, and any claim the evidence contradicts
is called out by name.

When to use this skill

Whenever asked to prepare, cut, or ship a release for a specific GitHub
repository.

Step-by-step workflow

Find the last tag. Use the GitHub tool. If there is no tag yet, use
the first commit as the starting point and say so.

List commits since that tag. Pull messages, authors, and diffs where
available. Treat each commit message as a CLAIM — not yet verified.

Clone and test in the sandbox. Run the repo's real test command
(check package.json, or the language's usual convention). Capture the
actual output. This is your first piece of EVIDENCE.

Gate on test results, with a real explanation.

Any failure -> stop. Identify which commit most likely caused it and
explain why in plain language, then stop completely — no contract, no
notes, no versioning, no approval step. This refusal-with-reasoning IS
the deliverable for this path.

All pass -> continue.

Build and validate the Release Contract. For this repository, the
contract is:

existing public APIs remain callable, unless a breaking release is
explicitly intended

existing tests continue to pass

new functionality does not break existing behavior

no release-blocking regression is detected

the proposed version matches the actual semantic impact

For every contract item, report STATUS (PASS / FAIL / UNKNOWN) and the
concrete EVIDENCE behind it — never PASS on a commit message's word
alone. The proposed-version item may remain UNKNOWN until semantic
analysis is reached.

If any release-blocking item is FAIL, mark the release BLOCKED, name the
evidence that caused it, and stop. Do not classify, draft final notes,
propose a final version, or ask for approval on a blocked contract.
A required UNKNOWN must be resolved before claiming RELEASE READY.

Compare claim against evidence for anything material. For each
commit that affects a contract item, state the CLAIM (what the message
says) next to the EVIDENCE (what the diff/tests/sandbox actually show).
Where they disagree, say so using the exact phrase "claim overridden by
evidence" — this is the skill's signature moment and should never be
softened into a hedge. Maintain a short, numbered EVIDENCE LEDGER (E1,
E2, ...) across the run, and when you state a decision, cite which
ledger entries it rests on (e.g. "DECISION BASIS: E2 + E3 + E4").

Classify commits — script first, your judgment second. Run
scripts/classify.py on the commit list as a rough mechanical triage
pass (it only matches keyword patterns). Then personally review every
commit's real message and diff against the evidence ledger, especially
ones the script marked "other" or low-confidence, or ones with
unconventional phrasing. Where your read differs from the script's, say
so explicitly and show the chain: script triage -> actual diff ->
contract result -> semantic impact -> proposed version (e.g. "PATCH ->
OVERRIDDEN -> MAJOR"). Your final semver-bump proposal is your judgment,
informed by but not bound to the script, and reasoned fresh from the
current repository state each run.

Check external release impact, then interpret it. Run
scripts/blast_radius.py <package_name> <registry> for a raw external
signal (registry downloads / known dependents), and add it to the
evidence ledger. This is deliberately an OUTSIDE-the-repo signal — how
many real consumers this release reaches — not an internal
code-dependency graph. Then say what that number means for THIS release
given what actually changed — low risk despite a big number if the
change is internal-only; high risk even on a small number if it touches
a widely-used public function. If the signal is unavailable, say so.

Draft release notes. Breaking Changes / Features / Fixes, plain
language, referencing real commits and the evidence behind each
classification.

Present and pause for approval. Show: the Release Contract
(item-by-item, with evidence), the evidence ledger, proposed version +
reasoning (including any script overrides), the interpreted
blast-radius line, an overall risk read, and the release notes. Ask
explicitly: "Approve publishing v<X.Y.Z>? (yes/no)."

On approval, publish in two steps. First, use the
create_or_update_file GitHub tool to commit the release notes into
CHANGELOG.md (this tool is configured to require approval itself — a
real, tool-level gate, not just a prompt instruction). Second, once that
commit succeeds, run git tag v<X.Y.Z> && git push origin v<X.Y.Z> in
the sandbox to create the actual tag. Report back what was created,
with links if available. Do not attempt npm/PyPI publishing — out of
scope.

Final Release Contract gate

Before asking for human approval, every required contract item must be
resolved.

The release may be shown as RELEASE READY only when:

no release-blocking contract item is FAIL

no required contract item is UNKNOWN

tests have passed

semantic impact has been reasoned from the actual evidence

the proposed version matches that semantic impact

Use a visible final state such as:

RELEASE CONTRACT
✓ Public API compatibility — PASS
✓ Existing tests — PASS
✓ Existing behavior — PASS
✓ No release-blocking regression — PASS
✓ SemVer matches semantic impact — PASS

DECISION: RELEASE READY
PROPOSED VERSION: vX.Y.Z
DECISION BASIS: E2 + E3 + E4 + E5
HUMAN APPROVAL REQUIRED

For a blocked candidate:

RELEASE CONTRACT
✗ Public API compatibility — FAIL
✗ Existing tests — FAIL
? SemVer — UNKNOWN

DECISION: RELEASE BLOCKED
DECISION BASIS: E2 + E3 + E4
STOP

References / related concepts

The positioning references already identified for this skill are:

semantic-release — conventional automated versioning/release workflow

CodeRabbit — upstream code/PR review and diff-level analysis

These are contextual references only. They are not evidence for an individual
release decision.

Files in this skill

scripts/classify.py — rough keyword-based triage only, not authoritative

scripts/blast_radius.py — raw registry download-count lookup only, not
a risk assessment on its own

Guardrails

Never fabricate test results, commit data, download numbers, or evidence.
Mark anything unverifiable as UNKNOWN rather than assuming it's fine.

Never mark a Release Contract item PASS merely because a commit message
claims it — it must be backed by diff, test, or sandbox evidence.

Use the exact phrase "claim overridden by evidence" only when there is a
real, demonstrable disagreement between a commit message and the
repository evidence — not as a stock phrase.

Never call create_or_update_file, tag, or push without an explicit human
"yes" after the approval step.

Never ask for approval while a required contract item is FAIL or UNKNOWN.

Never print or log API keys/tokens.
