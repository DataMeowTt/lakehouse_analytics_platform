-- Không có dữ liệu return/cancellation thật (Olist gốc và generator đều không sinh bảng return
-- riêng) — dùng order_status = 'canceled' làm proxy gần đúng nhất cho "đơn bị trả/huỷ".
select
    order_id,
    customer_unique_id,
    order_purchase_timestamp,
    order_purchase_date,
    payment_total_value as returned_amount

from {{ ref('int_orders_joined') }}
where order_status = 'canceled'
