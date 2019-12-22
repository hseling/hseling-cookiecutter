all: test

clean:
	rm -rf /tmp/hseling-repo-your-application/

test: clean
	cookiecutter . --output-dir /tmp --no-input && \
	cd /tmp/hseling-repo-your-application/hseling_api_your_application && \
	make test
