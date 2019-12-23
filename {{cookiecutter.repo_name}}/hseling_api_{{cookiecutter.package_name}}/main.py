from hseling_api_{{cookiecutter.package_name}}.main import (
    app,
{%- if cookiecutter.celery %}
    celery{%- endif %}
)
