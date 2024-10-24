{% if not category.name.is_other %}
## {{ category.name }}
{% endif %}
{% for subcategory in subcategories %}
{{subcategory.rendered}}
{% endfor %}
