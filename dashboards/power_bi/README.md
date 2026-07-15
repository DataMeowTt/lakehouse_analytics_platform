# Power BI Dashboards

`dashboard.pbix` connects to BigQuery dataset `retail_lakehouse` (Import mode).
Currently covers 2 of the 4 planned dashboards: **Executive** and **Customer**
(Product and Seller are not built yet — see `step-to-step.md` Ngày 25).

All currency figures (`GMV`, `AOV`, `LTV`, `Monetary`) are in the same unit as
`payment_value` in the pipeline — Brazilian Real, following the Olist source
dataset. No currency symbol is rendered on the visuals, but every dollar-labelled
field should be read as that currency.

## Executive Dashboard

Shows overall sales performance: 3 KPI cards (**Overall AOV** — average order
value, a weighted average = total GMV ÷ total orders, not an average of daily
AOVs; **Total Orders** — distinct order count; **Total GMV** — gross merchandise
value, summed across all orders regardless of status) plus two trend lines,
**Revenue by Year** and **Revenue by Month**, both showing GMV over time.

## Customer Dashboard

Shows customer value and segmentation: a distribution chart of **customers by
LTV** (lifetime total spend per customer), a **Top Customers** table (highest
LTV, with order count), and two RFM views — **Avg Monetary by RFM segment** and
**Total Customers by RFM segment** (share of customers in each of the 6
segments: Champion, Loyal, At Risk, Regular, New Customer, Lost).

## Reading the numbers — data caveats

This is synthetic Dev-tier data, not real transactions, so a few patterns on the
dashboards are generator artifacts rather than real business signal:

- **Revenue by Year/Month looks flat with no real growth or seasonality** — order
  timestamps are sampled uniformly across the full 2019–2026 range, so there is no
  built-in trend. The recurring yearly dip lines up with February simply having
  fewer days than other months, not a real seasonal effect.
- **LTV and order counts are extremely right-skewed** — a handful of customers
  have disproportionately many orders (into the thousands) because the generator
  intentionally skews customer selection (Zipf-like), not because any real
  customer behaves that way.
- **RFM segment labels are a rule-based classification** (see
  `macros/classify_rfm_segment.sql`), not a machine-learned model — read them as
  "customers that score high/low on Recency, Frequency, Monetary," not a
  guaranteed prediction of future behavior.

## Not yet built

- **Product Dashboard** (Top Products/Categories, Return Rate)
- **Seller Dashboard** (Revenue, Delivery Time, Rating, Refund Rate)
