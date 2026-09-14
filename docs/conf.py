"""Sphinx configuration."""

from __future__ import annotations

import datetime
import pathlib
import sys
from importlib import metadata

import django
from django.conf import settings

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

# Autodoc imports the package, and the package imports Django, which refuses
# to do anything without configured settings. A throwaway configuration with
# no database is enough: nothing documented here touches one at import time.
if not settings.configured:
    settings.configure(
        BASE_DIR=pathlib.Path(__file__).resolve().parent.parent,
        DATABASES={},
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.messages',
            'django.contrib.sessions',
            'django_admin_generator',
        ],
        USE_TZ=True,
    )
    django.setup()

project: str = 'Django Admin Generator'
author: str = 'Rick van Hattem'
copyright = (  # noqa: A001
    f'2014-{datetime.datetime.now(tz=datetime.timezone.utc):%Y}, {author}'
)
release: str = metadata.version('django-admin-generator')
version: str = '.'.join(release.split('.')[:2])

extensions: list[str] = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

napoleon_google_docstring: bool = True
napoleon_numpy_docstring: bool = False

autodoc_typehints: str = 'description'
autodoc_member_order: str = 'bysource'
autodoc_default_options: dict[str, object] = {
    'members': True,
    'show-inheritance': True,
}
# `reversion` and `django_json_widget` are optional integrations that the docs
# environment does not install.
autodoc_mock_imports: list[str] = ['django_json_widget', 'reversion']

html_theme: str = 'furo'
html_title: str = 'Django Admin Generator'
html_static_path: list[str] = ['_static']
html_favicon: str = '_static/favicon.svg'
html_css_files: list[str] = ['admin-generator.css']
exclude_patterns: list[str] = ['_build']

html_theme_options: dict[str, object] = {
    'light_logo': 'admin-generator-light.svg',
    'dark_logo': 'admin-generator-dark.svg',
    'sidebar_hide_name': True,
    'light_css_variables': {
        'color-brand-primary': '#0c4b33',
        'color-brand-content': '#0c4b33',
    },
    'dark_css_variables': {
        'color-brand-primary': '#44b78b',
        'color-brand-content': '#44b78b',
    },
}

intersphinx_mapping: dict[str, tuple[str, str | None]] = {
    'python': ('https://docs.python.org/3', None),
    'django': (
        'https://docs.djangoproject.com/en/stable/',
        'https://docs.djangoproject.com/en/stable/_objects/',
    ),
}
