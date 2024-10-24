{% if not category.name.is_other %}
## {{ category.name }}
Here, we visualize the data in a nice way.
{% endif %}
{% for subcategory in subcategories %}
{{subcategory.rendered}}
{% endfor %}
