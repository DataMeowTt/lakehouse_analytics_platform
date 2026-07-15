select
    order_id,
    cast(order_item_id as int64) as order_item_id,
    product_id,
    seller_id,
    cast(price as float64) as price,
    _generated_at,
    _generator_run_id

from {{ source('staging_raw', 'order_items') if target.name != 'ci' else ref('order_items') }}
