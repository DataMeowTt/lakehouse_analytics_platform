with reference_date as (
    select
        date_add(cast(max(order_purchase_timestamp) as date), interval 1 day) as analysis_date
    from {{ ref('fact_orders') }}
),

customer_rfm_raw as (
    select
        c.customer_unique_id,
        date_diff(
            (select analysis_date from reference_date),
            cast(c.last_purchase_at as date),
            day
        ) as recency_days,
        c.order_count as frequency,
        c.total_spent as monetary

    from {{ ref('int_customer_orders') }} c
),

customer_rfm_scored as (
    select
        customer_unique_id,
        recency_days,
        frequency,
        monetary,
        ntile(5) over (order by recency_days desc) as r_score,
        ntile(5) over (order by frequency asc) as f_score,
        ntile(5) over (order by monetary asc) as m_score

    from customer_rfm_raw
)

select
    customer_unique_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    {{ classify_rfm_segment('r_score', 'f_score', 'm_score') }} as rfm_segment

from customer_rfm_scored
