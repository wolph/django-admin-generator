"""String templates used to render the generated ``admin.py`` source."""

import typing

PRINT_IMPORTS_BASE: typing.Final[str] = """
from django.contrib import admin
{imports}

class ModelAdminBase({model_admin_class}):
    formfield_overrides = {formfield_overrides}
"""

VERSION_ADMIN_CLASS: typing.Final[str] = """
class VersionModelAdminBase({reversion_admin_class}, ModelAdminBase):
    pass
"""

PRINT_ADMIN_CLASS: typing.Final[str] = """

class {name}Admin({base_class}):
{class_}
"""

PRINT_ADMIN_REGISTRATION_METHOD: typing.Final[str] = """

def _register(model, admin_class):
    admin.site.register(model, admin_class)

"""

PRINT_ADMIN_REGISTRATION: typing.Final[str] = """
_register({full_name}, {name}Admin)"""

PRINT_ADMIN_REGISTRATION_LONG: typing.Final[str] = """
_register(
    {full_name},
    {name}Admin)"""

PRINT_ADMIN_PROPERTY: typing.Final[str] = """
    {key} = {value}"""
