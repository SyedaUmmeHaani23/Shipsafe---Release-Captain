# ShipSafe --- AI Release Decision & Safety Agent

> **Don't just automate the release. Prove it's safe to ship.**

ShipSafe is an AI-powered **release decision and safety agent** built
for the TrueFoundry × Polaris **Agents That Act** hackathon.

Instead of blindly automating a release, ShipSafe investigates the
repository, verifies what actually changed, runs real tests inside an
isolated sandbox, evaluates release impact, and stops before
irreversible actions require human approval.

## The Core Idea

A commit message is a **claim**.

The repository is the **evidence**.

ShipSafe follows one principle:

> **Trust Nothing. Verify Everything.**

It does not assume that a commit prefix or developer description
accurately represents the code change. It checks the real Git history,
actual diff, existing contracts and tests, and sandbox execution results
before making a release recommendation.

When a claim conflicts with evidence:

> **Claim overridden by evidence.**

## What ShipSafe Does

Given a GitHub repository and its latest release, ShipSafe:

1.  Identifies the latest release tag.
2.  Reads the commits since that release.
3.  Treats commit messages as claims rather than facts.
4.  Inspects the actual code changes and diffs.
5.  Checks existing APIs, tests, and repository behavior.
6.  Runs the repository tests inside a Daytona sandbox.
7.  Builds an evidence ledger from the investigation.
8.  Evaluates the repository against a Release Safety Contract.
9.  Determines the semantic impact of the changes.
10. Proposes an appropriate semantic version.
11. Drafts release notes and rollback considerations.
12. Stops before an irreversible release action.
13. Waits for explicit human approval before proceeding.

The goal is not simply to automate releasing.

The goal is to make the release decision **evidence-driven and
auditable**.

## Architecture

``` text
REAL GITHUB
     ↓
LATEST RELEASE TAG
     ↓
COMMITS / CLAIMS
     ↓
ACTUAL DIFF / EVIDENCE
     ↓
DAYTONA SANDBOX
     ↓
EVIDENCE LEDGER
     ↓
RELEASE CONTRACT
     ↓
SEMANTIC IMPACT
     ↓
PROPOSED VERSION
     ↓
HUMAN APPROVAL
     ↓
IRREVERSIBLE RELEASE ACTION
```

## Evidence Ledger

  -----------------------------------------------------------------------
  Evidence                            What is verified
  ----------------------------------- -----------------------------------
  **E1 --- Git History**              Release history, tags, commits, and
                                      chronology

  **E2 --- Actual Diff**              What the code really changed

  **E3 --- Existing Contract**        Existing APIs, tests, and expected
                                      behavior

  **E4 --- Sandbox**                  Real execution and test results

  **E5 --- External Impact**          Potential downstream or release
                                      impact
  -----------------------------------------------------------------------

## Release Safety Contract

ShipSafe evaluates the candidate release against explicit safety
conditions.

### RC1 --- Existing Public APIs

Existing public APIs must remain callable unless a breaking release is
explicitly intended.

### RC2 --- Existing Tests

Existing tests must continue to pass.

### RC3 --- Existing Behavior

New functionality must not unintentionally break existing behavior.

### RC4 --- Release-Blocking Regression

No known release-blocking regression may remain.

### RC5 --- Semantic Version

The proposed SemVer must match the **actual semantic impact** of the
change, not merely the commit prefix.

A failed contract item can block the release.

## The Safety Gate

ShipSafe deliberately separates **analysis** from **irreversible
action**.

``` text
ANALYZE
   ↓
VERIFY
   ↓
TEST
   ↓
CLASSIFY
   ↓
PREPARE RELEASE
   ↓
┌─────────────────────────────┐
│ HUMAN APPROVAL REQUIRED     │
└─────────────────────────────┘
   ↓
IRREVERSIBLE RELEASE ACTION
```

The agent does not treat a successful analysis as permission to publish.

The human remains the final release authority.

## Demonstration Repository

ShipSafe is demonstrated against a separate repository containing an intentionally messy release history.

**Demo repository:** [SyedaUmmeHaani23/shipsafe-demo](https://github.com/SyedaUmmeHaani23/shipsafe-demo)

The demo repository contains:

-   A released `v1.0.0` baseline
-   Subsequent feature changes
-   A misleading commit message
-   A public API compatibility regression
-   Existing tests that expose the regression

## Example: Claim vs Evidence

One demo change contains:

``` text
fix: remove getUser() helper, use fetchUser() instead
```

ShipSafe does not automatically trust that description.

It checks the actual repository state and discovers that an existing
test still depends on `get_user()`.

``` text
CLAIM
"remove getUser() helper"
        ↓
ACTUAL EVIDENCE
get_user() was removed
existing tests still import get_user()
        ↓
CLAIM OVERRIDDEN BY EVIDENCE
        ↓
TEST FAILURE
ImportError: cannot import name 'get_user'
        ↓
RELEASE CONTRACT FAILURE
RC1  Existing public API     FAIL
RC2  Existing tests          FAIL
RC3  Existing behavior      FAIL
RC4  Release-blocking issue  FAIL
        ↓
RELEASE BLOCKED
```

The agent explains the likely cause and stops.

After the compatibility issue is fixed, the tests can be rerun and the
release can be reassessed.

## Demo Flow

``` text
v1.0.0
  ↓
Real GitHub history
  ↓
Messy changes
  ↓
Misleading commit claim
  ↓
Actual diff inspection
  ↓
Daytona test execution
  ↓
Real test failure
  ↓
ShipSafe explains the failure
  ↓
RELEASE BLOCKED
  ↓
Developer restores compatibility
  ↓
Tests pass
  ↓
Semantic impact assessment
  ↓
Release notes + rollback plan
  ↓
HUMAN APPROVAL
  ↓
Only then: irreversible release action
```

## Technology Stack

-   **TrueForge** --- agent runtime and tool orchestration
-   **GitHub** --- repository history, tags, commits, source files, and
    change evidence
-   **Daytona** --- isolated sandbox execution
-   **ShipSafe Skill** --- procedural release investigation and safety
    workflow
-   **Python** --- supporting analysis scripts

Supporting scripts:

``` text
scripts/
├── blast_radius.py
└── classify.py
```

## Repository Structure

``` text
ShipSafe---Release-Captain/
│
├── README.md
│
└── shipsafe-release-captain/
    ├── SKILL.md
    └── scripts/
        ├── blast_radius.py
        └── classify.py
```

## Key Design Principles

### 1. Trust Nothing. Verify Everything.

Commit messages are useful context, not proof.

### 2. Evidence Before Action

The agent investigates the repository before proposing a release.

### 3. Failures Are Evidence

A failing test becomes part of the Evidence Ledger and can block the
release.

### 4. Human Approval Before Irreversible Actions

The agent prepares the release decision, but the final irreversible
action requires explicit human approval.

### 5. Explainability

The decision is traceable through:

``` text
Git history
→ actual diff
→ contract
→ sandbox result
→ semantic impact
→ release decision
```

## What Makes ShipSafe Different?

ShipSafe is not intended to be:

-   A generic code reviewer
-   A simple commit-message parser
-   A test runner with an LLM wrapper
-   A release-note generator
-   A fully autonomous "press deploy" bot

It is a **release decision agent**.

Its central responsibility is:

> **Determine whether the evidence supports shipping the release,
> explain why, and stop when the evidence says it is unsafe.**

## Safety Boundary

Before an irreversible action such as publishing or tagging a release,
the agent should present:

-   Proposed release version
-   Release impact
-   Test results
-   Release Contract status
-   Evidence Ledger
-   Known risks
-   Release notes
-   Rollback considerations

Then it waits for:

> **HUMAN APPROVAL REQUIRED**

No approval means no irreversible release action.

## Hackathon Context

Built for the **TrueFoundry × Polaris --- Agents That Act Hackathon**.

The project focuses on an agent that performs real work:

-   Reaches a real GitHub repository
-   Reads real release history
-   Inspects real code changes
-   Executes real tests in a sandbox
-   Builds an evidence-backed release decision
-   Stops at a meaningful human approval boundary

## AI Disclosure

AI assistants were used during development for:

-   Brainstorming
-   Architecture exploration
-   Documentation
-   Implementation assistance
-   Debugging
-   Refinement of the release workflow

The final ShipSafe workflow is designed to base release decisions on
real repository evidence and sandbox execution rather than trusting
generated assumptions.

## Security

Never commit secrets, API keys, access tokens, service-account
credentials, or private keys to this repository.

Use environment variables or the appropriate secret-management mechanism
for local development.

Credentials must not appear in:

-   GitHub repositories
-   README files
-   Screenshots
-   Demo videos
-   Logs
-   Public documentation

## Current Project Status

### Implemented

-   Real GitHub repository analysis
-   Latest release/tag discovery
-   Commit history inspection
-   Actual change verification
-   Evidence-based reasoning
-   Daytona sandbox test execution
-   Release Contract evaluation
-   Semantic impact assessment
-   Release blocking on verified regressions
-   Human approval boundary
-   Supporting blast-radius and classification scripts

### Planned / In Progress

-   Polished release command-center frontend
-   Visual Evidence Ledger
-   Release Contract dashboard
-   Commit intelligence view
-   Sandbox execution timeline
-   Human approval interface
-   Demo-oriented visualization of the release decision pipeline

## One-Line Pitch

> **ShipSafe is an AI release decision agent that verifies real code
> changes in a sandbox, proves whether a release is safe, and stops
> before irreversible action until a human approves it.**

## Project Philosophy

Software releases should not be trusted simply because a commit message
says they are safe.

**Claims can be wrong.**

**Evidence can expose the difference.**

ShipSafe puts that evidence between a code change and an irreversible
release.

> **Don't just automate the release. Prove it's safe to ship.**
