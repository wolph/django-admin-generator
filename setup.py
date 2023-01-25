import os
import sys
import setuptools
from setuptools.command.test import test as TestCommand

# To prevent importing about and thereby breaking the coverage info we use this
# exec hack
about = {}
with open('django_admin_generator/__about__.py') as fp:
    exec(fp.read(), about)


if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ('See http://pypi.python.org/pypi/' +
                        about['__package_name__'])


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


if __name__ == '__main__':
    setuptools.setup(
        name=about['__package_name__'],
        version=about['__version__'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        description=about['__description__'],
        url=about['__url__'],
        license='BSD',
        packages=setuptools.find_packages(),
        install_requires=[
            'django-utils2>=2.12.1',
            'six',
        ],
        extras_require={
            'docs': [
                'django>=3.2',
                'mock',
                'sphinx>=1.6.0',
            ],
            'tests': [
                'pytest',
                'pytest-cov',
                'pytest-django',
                'flake8',
            ],
        },
        long_description=long_description,
        cmdclass={'test': PyTest},
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
        ],
    )

