with order_items_total as (
    select order_id, sum(price) as items_total
    from {{ ref('stg_order_items') }}
    group by order_id
),

payments_total as (
    select order_id, sum(payment_value) as payments_total
    from {{ ref('fact_payments') }}
    group by order_id
)

select
    order_items_total.order_id,
    order_items_total.items_total,
    payments_total.payments_total
from order_items_total
join payments_total on order_items_total.order_id = payments_total.order_id
where abs(order_items_total.items_total - payments_total.payments_total) > 0.01
