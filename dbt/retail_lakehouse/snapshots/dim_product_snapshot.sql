{% snapshot dim_product_snapshot %}

{{
    config(
        target_schema=target.schema,
        unique_key='product_id',
        strategy='check',
        check_cols='all',
    )
}}

select * from {{ ref('dim_product') }}

{% endsnapshot %}
