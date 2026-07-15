select
    product_id,
    product_category_name,
    product_category_name_english

from {{ ref('stg_products') }}
