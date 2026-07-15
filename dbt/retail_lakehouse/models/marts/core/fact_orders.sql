{{ config(
    materialized='incremental',
    unique_key='order_id',
    partition_by={'field': 'order_purchase_date', 'data_type': 'date'},
    incremental_strategy='insert_overwrite'
) }}

select
    order_id,
    customer_unique_id,
    order_status,
    order_purchase_timestamp,
    order_purchase_date,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    item_count,
    item_total_value,
    payment_total_value

from {{ ref('int_orders_joined') }}

{% if is_incremental() %}
where order_purchase_timestamp > (select max(order_purchase_timestamp) from {{ this }})
{% endif %}
