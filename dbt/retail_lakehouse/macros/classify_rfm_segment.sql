{% macro classify_rfm_segment(r_score, f_score, m_score) %}
    case
        when {{ r_score }} >= 4 and {{ f_score }} >= 4 and {{ m_score }} >= 4 then 'Champion'
        when {{ r_score }} <= 2 and {{ f_score }} >= 3 then 'At Risk'
        when {{ f_score }} >= 4 and {{ m_score }} >= 3 then 'Loyal'
        when {{ r_score }} >= 4 and {{ f_score }} <= 2 then 'New Customer'
        when {{ r_score }} <= 2 and {{ f_score }} <= 2 and {{ m_score }} <= 2 then 'Lost'
        else 'Regular'
    end
{% endmacro %}
