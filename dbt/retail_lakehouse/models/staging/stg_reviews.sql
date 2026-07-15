select
    review_id,
    order_id,
    cast(review_score as int64) as review_score,
    _generated_at,
    _generator_run_id

from {{ source('staging_raw', 'reviews') if target.name != 'ci' else ref('reviews') }}
