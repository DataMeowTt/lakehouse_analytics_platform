select
    order_id,
    customer_unique_id,
    order_status,
    cast(order_purchase_timestamp as timestamp) as order_purchase_timestamp,
    cast(order_purchase_date as date) as order_purchase_date,
    cast(order_approved_at as timestamp) as order_approved_at,
    cast(order_delivered_carrier_date as timestamp) as order_delivered_carrier_date,
    cast(order_delivered_customer_date as timestamp) as order_delivered_customer_date,
    cast(order_estimated_delivery_date as timestamp) as order_estimated_delivery_date,
    _generated_at,
    _generator_run_id

from {{ source('staging_raw', 'orders') if target.name != 'ci' else ref('orders') }}
