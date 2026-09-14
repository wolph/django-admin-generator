Integrations
============

Two optional packages change the generated file when they are installed.
Neither is a dependency of this one: the generator looks them up and stays
quiet when they are missing, so nothing you generate can import a package your
project does not have.

django-json-widget
------------------

If ``django_json_widget`` is importable, every generated file gets a base
class with a ``JSONField`` override, and each model admin inherits from it:

.. code-block:: python

    from django.contrib import admin
    from django_json_widget.widgets import JSONEditorWidget
    from django.db.models import JSONField

    class ModelAdminBase(admin.ModelAdmin):
        formfield_overrides = {JSONField: {'widget': JSONEditorWidget}}

That turns Django's raw ``textarea`` for a JSON column into an editor that
validates as you type. Suppress it with ``--disable-json-widget``, which
leaves ``ModelAdminBase`` in place with empty overrides.

django-reversion
----------------

Reversion support is opt-in, because version tracking writes a row on every
save. Ask for it with ``--enable-reversion``:

.. code-block:: console

    ./manage.py admin_generator blog --enable-reversion

A second base class is emitted, and matching models inherit from it instead:

.. code-block:: python

    from reversion.admin import VersionAdmin

    class VersionModelAdminBase(VersionAdmin, ModelAdminBase):
        pass

By default every model in the app matches. Restrict that with a regular
expression when only part of the app needs history:

.. code-block:: console

    ./manage.py admin_generator blog --enable-reversion \
        --reversion-admin-regex '^(Post|Comment)$'

The base class and its import are both configurable, which is what you want
when your project wraps ``VersionAdmin`` in something of its own:

.. code-block:: console

    ./manage.py admin_generator blog --enable-reversion \
        --reversion-admin-class AuditedVersionAdmin \
        --reversion-admin-class-import 'from myproject.admin import AuditedVersionAdmin'

.. note::

    ``--enable-reversion`` is a request, not a guarantee. If ``reversion`` is
    not importable the flag is ignored and a plain file is generated, so a
    missing package never produces source that fails to import.

Your own base class
-------------------

Projects that already have an admin base class can build on it instead of on
``admin.ModelAdmin``:

.. code-block:: console

    ./manage.py admin_generator blog \
        --admin-class BaseAdmin \
        --admin-class-import 'from myproject.admin import BaseAdmin'

The import is separate from the class name because the Django default needs no
import of its own. Leave ``--admin-class-import`` off and you get a file that
references a name nothing imported, so pass both or neither.
