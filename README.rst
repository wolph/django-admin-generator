Readme
======

Introduction
------------

.. image:: https://travis-ci.org/WoLpH/django-admin-generator.png?branch=master
    :alt: Test Status
    :target: https://travis-ci.org/WoLpH/django-admin-generator

.. image:: https://coveralls.io/repos/WoLpH/django-admin-generator/badge.png?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/r/WoLpH/django-admin-generator?branch=master

The Django Admin Generator is a project which can automatically generate
(scaffold) a Django Admin for you. By doing this it will introspect your
models and automatically generate an Admin with properties like:

 - `list_display` for all local fields
 - `list_filter` for foreign keys with few items
 - `raw_id_fields` for foreign keys with a lot of items
 - `search_fields` for name and `slug` fields
 - `prepopulated_fields` for `slug` fields
 - `date_hierarchy` for `created_at`, `updated_at` or `joined_at` fields

Install
-------

To install simply execute `python setup.py install` in the source directory or
`pip install django-admin-generator`.
If you want to run the tests first, run `py.test`

Usage
-----

To generate an admin for a given app:

    ./manage.py admin_generator <APP_NAME> >> <APP_NAME>/admin.py

To generate an admin for a given app with all models starting with user:

    ./manage.py admin_generator <APP_NAME> '^user' >> <APP_NAME>/admin.py

