import os
from base64 import b64decode, b64encode
from flask import Flask, jsonify, request
from logging import getLogger

{% if not cookiecutter.rest %}
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException
{% endif %}

from hseling_api_{{cookiecutter.package_name}} import boilerplate

from hseling_lib_{{cookiecutter.package_name}}.process import process_data
from hseling_lib_{{cookiecutter.package_name}}.query import query_data


app = Flask(__name__)
app.config['DEBUG'] = False
app.config['LOG_DIR'] = '/tmp/'
if os.environ.get('HSELING_API_{{cookiecutter.package_name.upper()}}_SETTINGS'):
    app.config.from_envvar('HSELING_API_{{cookiecutter.package_name.upper()}}_SETTINGS')

{% if cookiecutter.celery -%}
app.config.update(
    CELERY_BROKER_URL=boilerplate.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=boilerplate.CELERY_RESULT_BACKEND
)
celery = boilerplate.make_celery(app)
{%- endif %}

if not app.debug:
    import logging
    from logging.handlers import TimedRotatingFileHandler
    # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
    file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'hseling_api_{{cookiecutter.package_name}}.log'), 'midnight')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter('<%(asctime)s> <%(levelname)s> %(message)s'))
    app.logger.addHandler(file_handler)

log = getLogger(__name__)
{% if not cookiecutter.rest %}
app.register_blueprint(api.as_blueprint(), url_prefix="/rpc/")
{% endif %}

ALLOWED_EXTENSIONS = ['txt']


def do_process_task(file_ids_list):
    files_to_process = boilerplate.list_files(recursive=True,
                                              prefix=boilerplate.UPLOAD_PREFIX)
    if file_ids_list:
        files_to_process = [boilerplate.UPLOAD_PREFIX + file_id
                            for file_id in file_ids_list
                            if (boilerplate.UPLOAD_PREFIX + file_id)
                            in files_to_process]
    data_to_process = {file_id[len(boilerplate.UPLOAD_PREFIX):]:
                       boilerplate.get_file(file_id)
                       for file_id in files_to_process}
    processed_file_ids = list()
    for processed_file_id, contents in process_data(data_to_process):
        processed_file_ids.append(
            boilerplate.add_processed_file(
                processed_file_id,
                contents,
                extension='txt'
            ))
    return processed_file_ids

{% if cookiecutter.celery -%}
@celery.task
def process_task(file_ids_list=None):
    return do_process_task(file_ids_list)
{% endif -%}


@app.route('/api/healthz')
def healthz():
    app.logger.info('Health checked')
    return jsonify({"status": "ok", "message": "hseling-api-{{cookiecutter.package_uri_part}}"})

{% if cookiecutter.rest -%}
@app.route('/api/upload', methods=['GET', 'POST'])
def upload_endpoint():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": boilerplate.ERROR_NO_FILE_PART})
        upload_file = request.files['file']
        if upload_file.filename == '':
            return jsonify({"error": boilerplate.ERROR_NO_SELECTED_FILE})
        if upload_file and boilerplate.allowed_file(
                upload_file.filename,
                allowed_extensions=ALLOWED_EXTENSIONS):
            return jsonify(boilerplate.save_file(upload_file))
    return boilerplate.get_upload_form()
{%- else %}

@api.dispatcher.add_method
def upload_file(file_name, file_contents_base64):
    if not file_name:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_SELECTED_FILE_CODE, message=boilerplate.ERROR_NO_SELECTED_FILE)
    if not file_contents_base64:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_FILE_PART_CODE, message=boilerplate.ERROR_NO_FILE_PART)
    if not boilerplate.allowed_file(file_name, allowed_extensions=ALLOWED_EXTENSIONS):
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NOT_ALLOWED_CODE, message=boilerplate.ERROR_NOT_ALLOWED)
    try:
        file_contents = b64decode(file_contents_base64)
        file_size = len(file_contents)
    except TypeError:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_FILE_PART_CODE, message=boilerplate.ERROR_NO_FILE_PART)
    return boilerplate.save_file_simple(file_name, file_contents, file_size)
{%- endif %}

{% if cookiecutter.rest -%}
@app.route('/api/files/<path:file_id>')
def get_file_endpoint(file_id):
    if file_id in boilerplate.list_files(recursive=True):
        return boilerplate.get_file(file_id)
    return jsonify({'error': boilerplate.ERROR_NO_SUCH_FILE})
{%- else %}

@api.dispatcher.add_method
def get_file(file_id):
    if file_id not in boilerplate.list_files(recursive=True):
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_SUCH_FILE_CODE, message=boilerplate.ERROR_NO_SUCH_FILE)
    file_contents_base64 = None
    try:
        file_contents_base64 = b64encode(boilerplate.get_file(file_id)).decode("utf-8")
    except TypeError:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_FILE_PART_CODE, message=boilerplate.ERROR_NO_FILE_PART)
    return {"file_id": file_id,
            "file_contents_base64": file_contents_base64}
{%- endif %}

{% if cookiecutter.rest -%}
@app.route('/api/files')
def list_files_endpoint():
    return jsonify({'file_ids': boilerplate.list_files(recursive=True)})
{%- else %}

@api.dispatcher.add_method
def list_files():
    return {'file_ids': boilerplate.list_files(recursive=True)}
{%- endif %}

{% if cookiecutter.celery -%}
def do_process(file_ids):
    file_ids_list = file_ids and file_ids.split(",")
    task = process_task.delay(file_ids_list)
    return {"task_id": str(task)}
{%- else -%}
def do_process(file_ids):
    file_ids_list = file_ids and file_ids.split(",")
    result = do_process_task(file_ids_list)
    return {"result": result}
{%- endif %}

{% if cookiecutter.rest -%}
@app.route('/api/process')
@app.route("/api/process/<file_ids>")
def process_endpoint(file_ids=None):
    return jsonify(do_process(file_ids))
{%- else %}

@api.dispatcher.add_method
def process_files(file_ids):
    if not file_ids:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_FILE_PART_CODE, message=boilerplate.ERROR_NO_FILE_PART)
    if isinstance(file_ids, list):
        file_ids = ",".join(file_ids)
    return do_process(file_ids)
{%- endif %}


def do_query(file_id, query_type):
    if not query_type:
        return {"error": boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED}
    processed_file_id = boilerplate.PROCESSED_PREFIX + file_id
    if processed_file_id in boilerplate.list_files(recursive=True):
        return {
            "result": query_data({
                processed_file_id: boilerplate.get_file(processed_file_id)
            }, query_type=query_type)
        }
    return {"error": boilerplate.ERROR_NO_SUCH_FILE}

{% if cookiecutter.rest -%}
@app.route("/api/query/<path:file_id>")
def query_endpoint(file_id):
    query_type = request.args.get('type')
    return jsonify(do_query(file_id, query_type))
{%- else %}

@api.dispatcher.add_method
def query_file(file_id, query_type):
    result = do_query(file_id, query_type)
    if result.get("error") == boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_QUERY_TYPE_SPECIFIED_CODE, message=result.get("error"))
    elif result.get("error") == boilerplate.ERROR_NO_SUCH_FILE:
        raise JSONRPCDispatchException(code=boilerplate.ERROR_NO_SUCH_FILE_CODE, message=result.get("error"))
    return result
{%- endif %}

{% if cookiecutter.rest -%}
@app.route("/api/status/<task_id>")
def status_endpoint(task_id):
    return jsonify(boilerplate.get_task_status(task_id))
{%- else %}

@api.dispatcher.add_method
def get_task_status(task_id):
    return boilerplate.get_task_status(task_id)
{%- endif %}

{% if cookiecutter.mysql -%}
def do_test_mysql():
    conn = boilerplate.get_mysql_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name, column_name FROM INFORMATION_SCHEMA.COLUMNS")
    schema = dict()
    for table_name, column_name in cur.fetchall():
        schema.setdefault(table_name.decode('utf-8'), []).append(column_name)
    return {"schema": schema}

{% if cookiecutter.rest -%}
@app.route("/api/test_mysql")
def test_mysql_endpoint():
    return jsonify(do_test_mysql())
{%- else %}

@api.dispatcher.add_method
def test_mysql():
    return do_test_mysql()
{%- endif %}
{%- endif %}

{% if cookiecutter.rest -%}
def get_endpoints(ctx):
    def endpoint(name, description, active=True):
        return {
            "name": name,
            "description": description,
            "active": active
        }

    all_endpoints = [
        endpoint("root", boilerplate.ENDPOINT_ROOT),
        endpoint("scrap", boilerplate.ENDPOINT_SCRAP,
                 not ctx["restricted_mode"]),
        endpoint("upload", boilerplate.ENDPOINT_UPLOAD),
        endpoint("process", boilerplate.ENDPOINT_PROCESS),
        endpoint("query", boilerplate.ENDPOINT_QUERY),
        endpoint("status", boilerplate.ENDPOINT_STATUS)
    ]

    return {ep["name"]: ep for ep in all_endpoints if ep}


@app.route("/api/")
def main_endpoint():
    ctx = {"restricted_mode": boilerplate.RESTRICTED_MODE}
    return jsonify({"endpoints": get_endpoints(ctx)})
{%- endif %}

{% if not cookiecutter.rest -%}
@api.dispatcher.add_method
def add(a, b):
    return a + b
{%- endif %}


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)


__all__ = [app{%- if cookiecutter.celery -%}, celery{%- endif -%}]
