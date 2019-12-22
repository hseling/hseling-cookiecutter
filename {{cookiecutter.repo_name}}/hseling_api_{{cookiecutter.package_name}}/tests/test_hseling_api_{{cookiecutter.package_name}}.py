import unittest

import hseling_api_{{cookiecutter.package_name}}


class HSELing_API_{{cookiecutter.package_name.capitalize()}}TestCase(unittest.TestCase):

    def setUp(self):
        self.app = hseling_api_{{cookiecutter.package_name}}.app.test_client()

    def test_index(self):
        rv = self.app.get('/healthz')
        self.assertIn('Application {{cookiecutter.application_name}}', rv.data.decode())


if __name__ == '__main__':
    unittest.main()
