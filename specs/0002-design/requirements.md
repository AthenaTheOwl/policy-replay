# requirements - 0002-design

## scope

v0.1 ships one deterministic replay for a PJM capacity-market rule
fixture. It proves rule loading, pure translation, historical replay,
schema validation, and report rendering.

## requirements

- R-PR-013: `python -m policy_replay simulate` writes a replay result
  and markdown report.
- R-PR-014: The rule translator is a pure function.
- R-PR-015: Replays are byte-stable for the same inputs and seed.
- R-PR-016: The report contains no policy advocacy language.
- R-PR-017: Schema and sanity-bounds gates pass on committed artifacts.

