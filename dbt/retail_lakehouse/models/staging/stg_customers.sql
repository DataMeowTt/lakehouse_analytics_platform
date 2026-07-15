select
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state

from {{ source('staging_raw', 'customers') if target.name != 'ci' else ref('customers') }}
