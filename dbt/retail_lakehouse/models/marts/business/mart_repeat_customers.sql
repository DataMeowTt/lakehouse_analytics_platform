select
    customer_unique_id,
    order_count,
    order_count > 1 as is_repeat_customer

from {{ ref('int_customer_orders') }}
