# Review an assumption change before comparing counterfactuals

A rule replay has three distinct inputs: the source document, the interpretation
that turns it into parameters, and the historical dataset. A new filing can
change one without changing the others. Treating every update as a new filename
loses the reason two replay results differ.

Before editing a rule, retain its bytes and the historical snapshot. Write a small
change memo with the old and new rule references, the affected parameter, the
source passage supporting the interpretation, and the outcome expected to move.
Classify the change as a corrected reading, a different proposed rule, or new
historical data. The memo should distinguish sourced values from modeling
assumptions.

Run the same seed and historical snapshot for a parameter change. If the history
also changed, first replay the old rule against the new history so the data effect
can be inspected separately. Retain both results and their digests. A deterministic
reproduction establishes repeatability under those inputs; it does not establish
that the counterfactual matches what an actual market would have done.

For every important interpretation, state a falsification check: a published
worked example, a known limiting case, or a past change whose observed outcome
the model should reproduce within a declared tolerance. Keep calibration failures
in the review record. Do not turn a matching aggregate into a claim that all
auction or participant behavior has been validated.

This is an operating protocol for the existing rule/history/report boundary; the
current runner does not traverse dependencies or enforce semantic review for you.
The output remains a descriptive counterfactual screen. This note adds no current
market forecasts, valuation claims, policy recommendations or live filing data.
