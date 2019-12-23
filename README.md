# hseling-cookiecutter

This is Cookiecutter template to create repositories with Libraries, APIs and Web parts for HSELing project.

## Usage

Install [cookiecutter](https://github.com/audreyr/cookiecutter):

    pip install --user cookiecutter

Create your application from this template:

    cookiecutter https://github.com/hseling/hseling-cookiecutter.git

All set! Run the application:

    cd hseling-repo-your-application/hseling_api_your_application
    make run

And then open it at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Docker

Your can run full bundle like this:

    cd hseling-repo-your-application
    docker-compose build
    docker-compose up

# Contributions

... are welcome! Feel free to create a pull request to fix bugs or keep up to date.

If you do a change, use `make test` from root directory to test the updated template.

# License

MIT License. See LICENSE file.
