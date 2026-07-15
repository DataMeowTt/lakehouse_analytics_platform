select
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state

from {{ source('staging_raw', 'sellers') if target.name != 'ci' else ref('sellers') }}
