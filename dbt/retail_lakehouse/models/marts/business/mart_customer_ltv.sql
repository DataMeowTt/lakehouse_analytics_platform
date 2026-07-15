select
    customer_unique_id,
    total_spent as ltv

from {{ ref('int_customer_orders') }}
