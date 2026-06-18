# Django Admin Generator

[![CI](https://github.com/WoLpH/django-admin-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/WoLpH/django-admin-generator/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-admin-generator.svg)](https://pypi.org/project/django-admin-generator/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-admin-generator.svg)](https://pypi.org/project/django-admin-generator/)
[![Documentation Status](https://readthedocs.org/projects/django-admin-generator/badge/?version=latest)](https://django-admin-generator.readthedocs.io/en/latest/)

The Django Admin Generator is a project which can automatically generate
(scaffold) a Django Admin for you. By doing this it will introspect your
models and automatically generate an Admin with properties like:

- `list_display` for all local fields
- `list_filter` for foreign keys with few items
- `raw_id_fields` for foreign keys with a lot of items
- `search_fields` for `name` and `slug` fields
- `prepopulated_fields` for `slug` fields
- `date_hierarchy` for `created_at`, `updated_at` or `joined_at` fields

## Links

- **Documentation**: <https://django-admin-generator.readthedocs.io/en/latest/>
- **Source**: <https://github.com/WoLpH/django-admin-generator>
- **Bug reports**: <https://github.com/WoLpH/django-admin-generator/issues>
- **Package homepage**: <https://pypi.org/project/django-admin-generator/>
- **My blog**: <https://w.wol.ph/>

## Install

1. Install the package:

   ```sh
   pip install django-admin-generator
   ```

2. Add `django_admin_generator` to your `INSTALLED_APPS`.

## Usage

To generate an admin for a given app:

```sh
./manage.py admin_generator APP_NAME >> APP_NAME/admin.py
```

To generate an admin for a given app with all models starting with `user`:

```sh
./manage.py admin_generator APP_NAME '^user' >> APP_NAME/admin.py
```

To write the generated admin directly to each app's `admin.py`:

```sh
./manage.py admin_generator APP_NAME --write
```

Use `all` as the app name to generate admins for every local (i.e. not in
`site-packages`) app:

```sh
./manage.py admin_generator all
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) and
[tox](https://tox.wiki/):

```sh
uv sync --extra dev          # create the environment
uv run pytest                # run the tests
uv run ruff check .          # lint
uv run tox                   # full matrix (tests, lint, types, docs)
```
