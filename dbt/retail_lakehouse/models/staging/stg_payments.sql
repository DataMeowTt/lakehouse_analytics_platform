select
    order_id,
    cast(payment_sequential as int64) as payment_sequential,
    payment_type,
    cast(payment_installments as int64) as payment_installments,
    cast(payment_value as float64) as payment_value,
    _generated_at,
    _generator_run_id

from {{ source('staging_raw', 'payments') if target.name != 'ci' else ref('payments') }}
