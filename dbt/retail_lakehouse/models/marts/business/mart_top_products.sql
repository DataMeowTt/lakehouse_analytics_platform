select
    oi.product_id,
    p.product_category_name_english,
    count(distinct oi.order_id) as order_count,
    sum(oi.price) as total_revenue

from {{ ref('stg_order_items') }} oi
left join {{ ref('dim_product') }} p on oi.product_id = p.product_id
group by oi.product_id, p.product_category_name_english
