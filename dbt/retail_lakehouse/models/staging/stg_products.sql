select
    product_id,
    product_category_name,
    product_category_name_english

from {{ source('staging_raw', 'products') if target.name != 'ci' else ref('products') }}
