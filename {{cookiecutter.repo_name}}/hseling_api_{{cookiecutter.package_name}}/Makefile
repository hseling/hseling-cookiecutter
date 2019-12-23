all: run

clean:
	rm -rf venv && rm -rf *.egg-info && rm -rf dist && rm -rf *.log*

venv:
	virtualenv --python=python3 venv && venv/bin/pip install ../hseling_lib_{{cookiecutter.package_name}} && venv/bin/pip install .

run: venv
	FLASK_APP=hseling_api_{{cookiecutter.package_name}} venv/bin/flask run

test: venv
	HSELING_API_{{cookiecutter.package_name.upper()}}_SETTINGS=../settings.cfg venv/bin/python -m unittest discover -s tests

sdist: venv test
	venv/bin/python setup.py sdist
