select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    _generated_at,
    _generator_run_id

from {{ ref('stg_payments') }}
