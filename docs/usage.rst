Command reference
=================

Every flag ``admin_generator`` accepts, grouped by the job it does. The
authoritative list is always ``./manage.py admin_generator --help``, which is
generated from the same parser.

Arguments
---------

.. option:: app

    The app to generate admin definitions for. Accepts the short label
    (``blog``) or the full dotted path (``myproject.blog``). The literal value
    ``all`` generates for every local app, meaning every app outside
    ``site-packages`` and outside a virtualenv in the project directory.

.. option:: models

    Zero or more regular expressions, matched case-insensitively against model
    names. Only matching models are generated. Omit them for the whole app.

Output
------

.. option:: -w, --write

    Write to the app's ``admin.py`` instead of stdout. Without it the
    generated source goes to stdout and nothing on disk changes.

.. option:: -o OUTPUT, --output OUTPUT

    Output file name, ``admin.py`` by default. A bare name is resolved
    relative to the app's directory. A name containing a path separator is
    used as given.

.. option:: -f, --force

    Overwrite the output file if it already exists. Without ``-f`` or ``-a``
    an existing file aborts the run.

.. option:: -a, --append

    Append to the output file instead of replacing it. Useful for collecting
    several filtered runs into one file.

Heuristics
----------

These flags move the thresholds described in :doc:`heuristics`.

.. option:: -l THRESHOLD, --list-filter-threshold THRESHOLD

    A foreign key or field with fewer than this many distinct values becomes a
    ``list_filter`` entry. Defaults to 25.

.. option:: -r THRESHOLD, --raw-id-threshold THRESHOLD

    A foreign key with more than this many rows becomes a ``raw_id_fields``
    entry rather than a select box. Defaults to 100.

.. option:: --date-hierarchy-threshold THRESHOLD

    A model with fewer than this many rows may get a ``date_hierarchy``.
    Defaults to 250.

.. option:: -s NAME, --search-field NAME

    Add a field name that should end up in ``search_fields``. Repeatable, and
    added to the defaults ``name`` and ``slug``.

.. option:: -d NAME, --date-hierarchy NAME

    Add a field name that may be used as ``date_hierarchy``. Repeatable, and
    added to the defaults ``joined_at``, ``updated_at`` and ``created_at``.

.. option:: -p SPEC, --prepopulated-fields SPEC

    Add a ``field=other_field`` pair for ``prepopulated_fields``. Repeatable,
    and added to the default ``slug=name``.

.. option:: -n, --no-query-db

    Never query the database. Row counts are what decide between a dropdown
    filter and a raw id field, so this trades accuracy for speed and for the
    ability to run against an empty or unavailable database.

Integrations
------------

.. option:: --disable-json-widget

    Leave out the ``django-json-widget`` import and the ``JSONField``
    ``formfield_overrides``.

.. option:: --disable-auto-complete

    Never emit ``autocomplete_fields`` for many-to-many relations.

.. option:: --auto-complete FIELD

    Emit ``autocomplete_fields`` only for the named field. Repeatable.

.. option:: --enable-reversion

    Generate ``django-reversion`` support, giving matching models a
    ``VersionAdmin`` base class.

.. option:: --reversion-admin-regex REGEX

    Restrict reversion support to models matching this expression. Defaults to
    ``.*``.

.. option:: --reversion-admin-class CLASS

    Base class used for reversion-enabled models. Defaults to
    ``VersionAdmin``.

.. option:: --reversion-admin-class-import IMPORT

    The import statement emitted for that base class. Defaults to
    ``from reversion.admin import VersionAdmin``.

.. option:: --admin-class CLASS

    Base class for the generated ``ModelAdmin`` classes. Defaults to
    ``admin.ModelAdmin``.

.. option:: --admin-class-import IMPORT

    The import statement emitted for a non-default ``--admin-class``. Empty by
    default, because the Django base class is already imported.

Recipes
-------

Print one model's admin without touching the database:

.. code-block:: console

    ./manage.py admin_generator blog '^post$' --no-query-db

Regenerate the whole project with a stricter raw id threshold:

.. code-block:: console

    ./manage.py admin_generator all --write --force --raw-id-threshold 25

Collect two apps into one reviewed file:

.. code-block:: console

    ./manage.py admin_generator blog -o /tmp/admin.py -f
    ./manage.py admin_generator shop -o /tmp/admin.py -a

Build on a project-wide base class:

.. code-block:: console

    ./manage.py admin_generator blog \
        --admin-class BaseAdmin \
        --admin-class-import 'from myproject.admin import BaseAdmin'
