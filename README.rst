Readme
======

Introduction
------------

.. image:: https://travis-ci.org/WoLpH/django-admin-generator.svg?branch=master
    :alt: Test Status
    :target: https://travis-ci.org/WoLpH/django-admin-generator

.. image:: https://coveralls.io/repos/WoLpH/django-admin-generator/badge.svg?branch=master
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

Links
-----

* Documentation
    - http://django-admin-generator.readthedocs.org/en/latest/
* Source
    - https://github.com/WoLpH/django-admin-generator
* Bug reports 
    - https://github.com/WoLpH/django-admin-generator/issues
* Package homepage
    - https://pypi.python.org/pypi/django-admin-generator
* My blog
    - http://w.wol.ph/

Install
-------

To install:

 1. Run `pip install django-admin-generator` or execute `python setup.py install` in the source directory
 2. Add `django_admin_generator` to your `INSTALLED_APPS`
 
If you want to run the tests, run `py.test` (requires `pytest`)

Usage
-----

To generate an admin for a given app:

    ./manage.py admin_generator APP_NAME >> APP_NAME/admin.py

To generate an admin for a given app with all models starting with user:

    ./manage.py admin_generator APP_NAME '^user' >> APP_NAME/admin.py

