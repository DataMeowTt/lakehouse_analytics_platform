select
    customer_unique_id,
    count(distinct order_id) as order_count,
    sum(payment_total_value) as total_spent,
    max(order_purchase_timestamp) as last_purchase_at

from {{ ref('int_orders_joined') }}
group by customer_unique_id
