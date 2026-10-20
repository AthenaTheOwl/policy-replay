# PolicyReplay result - pjm-dec2025-capacity-reform

Rule: PJM December 2025 capacity-market reserve margin change
Markets: pjm.rpm

## outcome delta

- mean price delta: 4.401 USD/MW-day
- mean cleared MW delta: -2676.300
- reserve margin delta: 1.50 percentage points

## model

This is a fixed-elasticity screen. Each auction's clearing price is scaled by 1 + 1.5 x 0.035 and its cleared MW by 1 + 1.5 x -0.012. Elasticity source: translator BASELINE default; assumed, not sourced to a filing.

- price shift: +5.250% on every auction
- cleared MW shift: -1.800% on every auction

The history sets each auction's baseline level, so the rows below and the dollar and MW deltas depend on it. The percentage shift does not: it is the same on any history. The response does not depend on `reserve_margin_pct`; that column is shown for context. The elasticities are not estimated from these auctions.

## per auction

| auction year | lda | reserve margin % | baseline price | counterfactual price | baseline MW | counterfactual MW |
|---:|---|---:|---:|---:|---:|---:|
| 2018 | RTO | 16.2 | 140.00 | 147.35 | 154,000 | 151,228 |
| 2019 | RTO | 15.8 | 110.00 | 115.78 | 151,500 | 148,773 |
| 2020 | RTO | 14.9 | 50.00 | 52.62 | 148,200 | 145,532 |
| 2021 | RTO | 15.6 | 140.00 | 147.35 | 150,300 | 147,595 |
| 2022 | RTO | 14.3 | 34.13 | 35.92 | 144,900 | 142,292 |
| 2023 | RTO | 13.9 | 28.92 | 30.44 | 143,200 | 140,622 |

## references

- https://www.pjm.com/committees-and-groups/committees/mic
- https://www.ferc.gov/industries-data/electric/electric-power-markets/pjm

## methodology

The v0.1 screen applies the rule's reserve-margin delta through fixed elasticities to each auction in the checked-in PJM RPM fixture. It does not estimate a response from the history, clear a market, or run trials. It is a deterministic counterfactual screen, not a forecast.
