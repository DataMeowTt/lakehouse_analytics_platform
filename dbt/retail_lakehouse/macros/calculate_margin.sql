{% macro calculate_margin(revenue, cost) %}
    ({{ revenue }} - {{ cost }}) / nullif({{ revenue }}, 0)
{% endmacro %}
