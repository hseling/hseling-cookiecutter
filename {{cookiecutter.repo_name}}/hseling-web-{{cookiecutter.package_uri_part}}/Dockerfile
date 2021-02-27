FROM hseling/hseling-api-base:python3.6-alpine3.7 as hseling_web_build

LABEL maintainer="{{cookiecutter.maintainer}}"

RUN mkdir /dependencies
COPY ./hseling-web-{{cookiecutter.package_uri_part}}/requirements.txt /dependencies/requirements.txt
COPY ./hseling-web-{{cookiecutter.package_uri_part}}/setup.py /dependencies/setup.py

RUN pip install -r /dependencies/requirements.txt

FROM hseling/hseling-api-base:python3.6-alpine3.7 as hseling_web_production

COPY --from=hseling_web_build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=hseling_web_build /usr/lib/python3.6/site-packages /usr/lib/python3.6/site-packages

COPY --from=hseling_web_build /dependencies /dependencies

COPY ./hseling-web-{{cookiecutter.package_uri_part}}/hseling_web_{{cookiecutter.package_name}} /app/hseling_web_{{cookiecutter.package_name}}
COPY ./hseling-web-{{cookiecutter.package_uri_part}}/hseling_web_{{cookiecutter.package_name}}/static /app/static
COPY ./hseling-web-{{cookiecutter.package_uri_part}}/main.py /app/main.py

ENV HSELING_WEB_{{cookiecutter.package_name.upper()}}_SETTINGS="/app/hseling_web_{{cookiecutter.package_name}}/default_settings.py"

HEALTHCHECK CMD curl --fail http://localhost:8000/healthz || exit 1

EXPOSE 8000
