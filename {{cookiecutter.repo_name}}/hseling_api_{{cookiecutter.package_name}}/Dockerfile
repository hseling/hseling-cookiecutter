FROM hseling/hseling-api-base:python3.6-alpine3.7 as build

LABEL maintainer="{{cookiecutter.maintainer}}"

RUN mkdir /dependencies
COPY ./hseling_api_{{cookiecutter.package_name}}/requirements.txt /dependencies/requirements.txt
COPY ./hseling_api_{{cookiecutter.package_name}}/setup.py /dependencies/setup.py

RUN pip install -r /dependencies/requirements.txt

FROM hseling/hseling-api-base:python3.6-alpine3.7 as production

COPY --from=build /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
COPY --from=build /usr/lib/python3.6/site-packages /usr/lib/python3.6/site-packages

COPY --from=build /dependencies /dependencies

COPY ./hseling_lib_{{cookiecutter.package_name}} /dependencies/hseling_lib_{{cookiecutter.package_name}}
RUN pip install /dependencies/hseling_lib_{{cookiecutter.package_name}}

COPY ./hseling_api_{{cookiecutter.package_name}}/hseling_api_{{cookiecutter.package_name}} /app

ENV HSELING_API_YOUR_APPLICATION_SETTINGS="/app/default_settings.py"

HEALTHCHECK CMD curl --fail http://localhost/healthz || exit 1
