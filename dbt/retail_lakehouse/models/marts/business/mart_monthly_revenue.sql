select
    date_trunc(order_purchase_date, month) as order_purchase_month,
    count(distinct order_id) as total_orders,
    sum(payment_total_value) as gmv,
    round(sum(payment_total_value) / count(distinct order_id), 2) as aov

from {{ ref('fact_orders') }}
group by order_purchase_month
