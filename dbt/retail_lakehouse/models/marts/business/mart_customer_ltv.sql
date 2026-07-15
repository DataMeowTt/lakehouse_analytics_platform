select
    customer_unique_id,
    total_spent as ltv,
    order_count,
    first_purchase_at,
    last_purchase_at

from {{ ref('int_customer_orders') }}
