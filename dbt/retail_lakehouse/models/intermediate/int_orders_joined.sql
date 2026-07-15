{{ config(
    materialized='incremental',
    unique_key='order_id',
    partition_by={'field': 'order_purchase_date', 'data_type': 'date'},
    incremental_strategy='insert_overwrite'
) }}

with orders as (
    select * from {{ ref('stg_orders') }}

    {% if is_incremental() %}
    where order_purchase_timestamp > (select max(order_purchase_timestamp) from {{ this }})
    {% endif %}
),

order_items_agg as (
    select
        order_id,
        count(*) as item_count,
        sum(price) as item_total_value
    from {{ ref('stg_order_items') }}
    where order_id in (select order_id from orders)
    group by order_id
),

payments_agg as (
    select
        order_id,
        sum(payment_value) as payment_total_value
    from {{ ref('stg_payments') }}
    where order_id in (select order_id from orders)
    group by order_id
)

select
    orders.order_id,
    orders.customer_unique_id,
    orders.order_status,
    orders.order_purchase_timestamp,
    orders.order_purchase_date,
    orders.order_approved_at,
    orders.order_delivered_carrier_date,
    orders.order_delivered_customer_date,
    orders.order_estimated_delivery_date,
    order_items_agg.item_count,
    order_items_agg.item_total_value,
    payments_agg.payment_total_value

from orders
left join order_items_agg on orders.order_id = order_items_agg.order_id
left join payments_agg on orders.order_id = payments_agg.order_id
