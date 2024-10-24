{% if not category.name.is_other %}
## {{ category.name }}
This is some custom introduction text for the data generation section.
{% endif %}
{% for subcategory in subcategories %}
{{subcategory.rendered}}
{% endfor %}
