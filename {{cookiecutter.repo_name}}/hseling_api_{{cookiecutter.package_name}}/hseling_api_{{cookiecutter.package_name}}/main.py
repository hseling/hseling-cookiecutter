import os
from flask import Flask, jsonify

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['LOG_DIR'] = '/var/log/'
app.config.from_envvar('HSELING_API_{{cookiecutter.package_name.upper()}}_SETTINGS')

if not app.debug:
    import logging
    from logging.handlers import TimedRotatingFileHandler
    # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
    file_handler = TimedRotatingFileHandler(os.path.join(app.config['LOG_DIR'], 'hseling_api_{{cookiecutter.package_name}}.log'), 'midnight')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter('<%(asctime)s> <%(levelname)s> %(message)s'))
    app.logger.addHandler(file_handler)


@app.route('/healthz')
def healthz():
    app.logger.info('Health checked')
    return jsonify({"status": "ok", "message": "Application {{cookiecutter.application_name}}"})
