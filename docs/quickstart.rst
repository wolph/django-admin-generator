Quickstart
==========

You have a set of models and an empty ``admin.py``. Writing that file by hand
is half an hour of typing that a command can do in a second, so let the
command do it.

Install
-------

.. code-block:: console

    python -m pip install django-admin-generator

Add the app to your settings so Django picks up the management command:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_admin_generator',
    ]

.. tip::

    The app is only needed while you generate. Drop it from
    ``INSTALLED_APPS`` afterwards if you would rather not ship it, or keep it
    in a development-only settings module.

Generate
--------

The command takes an app label or a dotted app path and prints to stdout:

.. code-block:: console

    ./manage.py admin_generator blog

.. code-block:: python

    from django.contrib import admin
    from django_json_widget.widgets import JSONEditorWidget

    class ModelAdminBase(admin.ModelAdmin):
        formfield_overrides = {models.JSONField: {'widget': JSONEditorWidget}}


    class CategoryAdmin(ModelAdminBase):
        list_display = ('id', 'name', 'slug')
        search_fields = ('name', 'slug')
        prepopulated_fields = {'slug': ['name']}

Printing rather than writing is deliberate. You get to read the heuristics'
verdict before it touches your source tree.

Filter the models
-----------------

Trailing arguments are regular expressions matched against model names, so a
large app does not have to be generated whole:

.. code-block:: console

    ./manage.py admin_generator blog '^post'
    ./manage.py admin_generator blog '^post' '^comment'

Write the file
--------------

Once the output looks right, write it into the app:

.. code-block:: console

    ./manage.py admin_generator blog --write

``--write`` targets ``<app>/admin.py``. An existing file is left alone unless
you pass ``-f`` to overwrite it or ``-a`` to append, which keeps a careless
run from eating admin code you wrote by hand:

.. code-block:: console

    ./manage.py admin_generator blog -o admin.py -f   # overwrite
    ./manage.py admin_generator blog -o admin.py -a   # append

Do the whole project
--------------------

The literal app name ``all`` generates for every local app, which means every
app that lives inside your project directory rather than in ``site-packages``:

.. code-block:: console

    ./manage.py admin_generator all

.. note::

    "Local" is decided by path, not by convention. An app inside your project
    root counts, an app inside ``venv/``, ``.venv/`` or ``site-packages``
    does not. See :func:`~django_admin_generator.discovery.get_local_apps`.

Where to go next
----------------

The defaults are opinionated but every threshold behind them is a flag. Read
:doc:`heuristics` for what the generator decides and how to shift it, or
:doc:`usage` for the full option list.

.. tip::

    Generating models from a legacy database with Django's ``inspectdb`` and
    then generating the admin from those models gets you a working interface
    over an inherited schema in two commands.
