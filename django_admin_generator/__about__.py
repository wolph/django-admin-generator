import typing
from importlib.metadata import (
    PackageNotFoundError,
    version as _version,
)

try:
    __version__: typing.Final[str] = _version('django-admin-generator')
except PackageNotFoundError:
    __version__ = '0.0.0'  # type: ignore[misc]

__package_name__: typing.Final[str] = 'django-admin-generator'
__import_name__: typing.Final[str] = 'django_admin_generator'
__author__: typing.Final[str] = 'Rick van Hattem'
__author_email__: typing.Final[str] = 'Wolph@Wol.ph'
__description__: typing.Final[str] = (
    'Django Admin Generator is a management command to automatically'
    ' generate a Django `admin.py` file for given apps/models.'
)
__url__: typing.Final[str] = 'https://github.com/WoLpH/django-admin-generator/'
