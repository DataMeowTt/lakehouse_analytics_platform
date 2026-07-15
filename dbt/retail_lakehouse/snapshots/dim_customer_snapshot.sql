{% snapshot dim_customer_snapshot %}

{{
    config(
        target_schema=target.schema,
        unique_key='customer_unique_id',
        strategy='check',
        check_cols='all',
    )
}}

select * from {{ ref('dim_customer') }}

{% endsnapshot %}
