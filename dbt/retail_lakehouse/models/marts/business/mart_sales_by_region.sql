select
    c.customer_state,
    count(distinct o.order_id) as total_orders,
    sum(o.payment_total_value) as gmv

from {{ ref('fact_orders') }} o
left join {{ ref('dim_customer') }} c on o.customer_unique_id = c.customer_unique_id
group by c.customer_state
