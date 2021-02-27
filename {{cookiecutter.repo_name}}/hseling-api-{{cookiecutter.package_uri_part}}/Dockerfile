FROM hseling/hseling-api-base:python3.6-alpine3.7 as hseling_api_build

LABEL maintainer="{{cookiecutter.maintainer}}"

RUN mkdir /dependencies
COPY ./hseling-api-{{cookiecutter.package_uri_part}}/requirements.txt /dependencies/requirements.txt
COPY ./hseling-api-{{cookiecutter.package_uri_part}}/setup.py /dependencies/setup.py

RUN pip install -r /dependencies/requirements.txt

FROM hseling/hseling-api-base:python3.6-alpine3.7 as production

COPY --from=hseling_api_build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=hseling_api_build /usr/lib/python3.6/site-packages /usr/lib/python3.6/site-packages

COPY --from=hseling_api_build /dependencies /dependencies

COPY ./hseling-lib-{{cookiecutter.package_uri_part}} /dependencies/hseling-lib-{{cookiecutter.package_uri_part}}
RUN pip install /dependencies/hseling-lib-{{cookiecutter.package_uri_part}}

COPY ./hseling-api-{{cookiecutter.package_uri_part}}/hseling_api_{{cookiecutter.package_name}} /app/hseling_api_{{cookiecutter.package_name}}
COPY ./hseling-api-{{cookiecutter.package_uri_part}}/main.py /app/main.py

RUN mkdir -p /data

ENV HSELING_API_{{cookiecutter.package_name.upper()}}_SETTINGS="/app/hseling_api_{{cookiecutter.package_name}}/default_settings.py"

HEALTHCHECK CMD curl --fail http://localhost:5000/healthz || exit 1

