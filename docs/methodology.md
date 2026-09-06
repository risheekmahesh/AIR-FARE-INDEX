# APIx methodology

## Scope

APIx is a demonstration of an automated airfare price index for six high-volume domestic city-pairs. The repository uses synthetic fares so the full pipeline is reproducible without scraping or credentials.

## Observation model

Each observation identifies a route, airline, travel date, booking date, advance-purchase window, fare class, fare components, source, and collection timestamp. `total_fare` is the sum of base fare, taxes, UDF, and convenience fee.

## Cleaning

The cleaning module applies three deterministic steps:

1. Numeric missing values are replaced with the column median; categorical missing values become `Unknown`.
2. Quotes are deduplicated on route, airline, travel date, booking date, advance window, and fare class, retaining the latest record.
3. Extreme total fares are removed using a 1.5×IQR fence. In production, the fence should be monitored by route and lead-time window rather than applied globally.

## Normalization and aggregation

For each route, the median total fare across the observation history is the reference price. The route index for period `t` is:

`I(r,t) = mean fare(r,t) / median fare(r,history) × 100`

The basket index is:

`APIx(t) = Σr w(r) I(r,t) / Σr w(r)`

where the fixed route weights are DEL-BOM 24%, DEL-BLR 23%, BOM-BLR 18%, DEL-CCU 14%, BLR-HYD 11%, and MAA-DEL 10%. These weights mirror relative passenger-traffic proportions across major domestic sectors and are inspired by DGCA passenger-traffic reporting; they are not an official CPI or MoSPI weighting scheme.

Daily values use booking date as the observation period. Weekly values group daily values by Monday-starting calendar week. Monthly values group by calendar month. Changes are period-over-period percentage movement.

## Interpretation

An index value above 100 means the observed basket is more expensive than its route-normalized reference level. The lead-time curve is descriptive: it shows the relationship between time-to-departure and mean observed fare in the demo fixture, not a causal estimate.

## Production controls

A production implementation should version the basket and weights, preserve raw immutable quotes, track source freshness, publish confidence intervals and sample counts, use official DGCA/MoSPI methodology approvals, and maintain a revision calendar. Synthetic data must never be represented as a live official statistic.
