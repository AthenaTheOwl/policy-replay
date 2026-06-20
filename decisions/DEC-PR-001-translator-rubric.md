---
id: DEC-PR-001-translator-rubric
spec: specs/0002-design/
requirement: R-PR-014
date: 2026-06-20
status: approved
reversible: true
decision: |
  Translate rule specs into explicit numeric parameter overrides before any
  replay runs.
alternatives:
  - label: encode rule logic directly inside the simulator
    rejected_because: |
      Hidden rule logic makes it hard to audit which text changed which
      simulation parameter.
  - label: store only free-text rule summaries
    rejected_because: |
      Free text cannot drive deterministic replay.
rationale: |
  Keeping translation pure and explicit makes the replay result reproducible
  and gives reviewers a narrow place to challenge assumptions.
evidence:
  - kind: spec
    ref: specs/0002-design/
rollback: |
  Replace the flat override map with typed parameter objects after more rule
  families land.
---

