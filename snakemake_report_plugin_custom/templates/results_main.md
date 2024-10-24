# {{title}}

Report generated on: {{ now }}
{{ workflow_description }}

## Results
{% for category, subcategories in results.items() %}
{{ category.rendered }}
{% endfor %}