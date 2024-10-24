{% if not subcategory.is_other %}
## {{ subcategory.name }}
{% endif %}
{% for file in files %}
{{file}}
{% endfor %}

