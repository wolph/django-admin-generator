<h1 align="center">Django Admin Generator</h1>

<p align="center"><strong>Scaffold a complete, sensible Django admin for your models — automatically.</strong></p>

[![CI](https://github.com/WoLpH/django-admin-generator/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/WoLpH/django-admin-generator/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/django-admin-generator.svg)](https://pypi.org/project/django-admin-generator/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-admin-generator.svg)](https://pypi.org/project/django-admin-generator/)
[![Downloads](https://img.shields.io/pypi/dm/django-admin-generator.svg)](https://pypi.org/project/django-admin-generator/)
[![Documentation](https://readthedocs.org/projects/django-admin-generator/badge/?version=latest)](https://django-admin-generator.readthedocs.io/en/latest/)
[![License](https://img.shields.io/pypi/l/django-admin-generator.svg)](https://github.com/WoLpH/django-admin-generator/blob/develop/LICENSE)

`django-admin-generator` is a management command that introspects your models
and writes a ready-to-use `admin.py` — `list_display`, `list_filter`,
`search_fields`, `raw_id_fields`, `date_hierarchy`, `prepopulated_fields` and
autocomplete — so you don't have to hand-write any of it.

![Auto-generated changelist](https://raw.githubusercontent.com/WoLpH/django-admin-generator/develop/docs/images/changelist.png)

*The list view above — columns, a filter sidebar, and a date drill-down — came
straight from the models, with zero hand-written admin code.*

## Quick start

```sh
pip install django-admin-generator
```

Add `django_admin_generator` to your `INSTALLED_APPS`, then generate an admin
and write it to the app's `admin.py`:

```sh
./manage.py admin_generator <app> --write
```

Reload the Django admin — your models are fully wired up.

## What gets generated

For every model, the generator inspects the fields and picks sensible options:

| Model trait | Generated option |
| --- | --- |
| All local fields | `list_display` |
| `DateField`, `BooleanField`, low-cardinality fields & foreign keys | `list_filter` |
| Foreign key to a large table (≥ `raw_id_threshold`, default 100) | `raw_id_fields` |
| `ManyToManyField` | `autocomplete_fields` (or `raw_id_fields`) |
| `name` / `slug` fields | `search_fields` |
| `slug` field | `prepopulated_fields` (from `name`/`title`) |
| `created_at` / `updated_at` / `joined_at` | `date_hierarchy` |
| `TextField` / `JSONField` / `BinaryField` / `FileField` | shown, but kept out of `list_filter` (DISTINCT is unsafe on some databases) |

The result is plain, readable code you can keep or tweak:

```python
class PostAdmin(ModelAdminBase):
    list_display = (
        'id', 'title', 'slug', 'body', 'created_at',
        'published_at', 'is_published', 'author', 'category',
    )
    list_filter = ('created_at', 'published_at', 'is_published', 'author', 'category')
    autocomplete_fields = ('tags',)
    search_fields = ('slug',)
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'created_at'
```

…which produces a fully-wired add/change form — prepopulated slugs,
autocomplete for relations, the right widgets everywhere:

![Auto-generated add form](https://raw.githubusercontent.com/WoLpH/django-admin-generator/develop/docs/images/add-form.png)

## Usage

By default the output is printed to stdout so you can review it before writing:

```sh
./manage.py admin_generator <app>                 # print to stdout
./manage.py admin_generator <app> '^user'         # only models matching a regex
./manage.py admin_generator <app> --write         # write <app>/admin.py
./manage.py admin_generator <app> -o admin.py -f  # custom output file, overwrite
./manage.py admin_generator all                   # every local (non site-packages) app
```

Handy options:

| Option | Effect |
| --- | --- |
| `-w`, `--write` | write to the app's `admin.py` (otherwise stdout) |
| `-o/--output`, `-f/--force`, `-a/--append` | output-file handling |
| `-l/--list-filter-threshold`, `-r/--raw-id-threshold`, `--date-hierarchy-threshold` | tune the heuristics |
| `-s/--search-field`, `-d/--date-hierarchy`, `-p/--prepopulated-fields` | add extra field names |
| `-n/--no-query-db` | don't query the database for row counts |
| `--enable-reversion`, `--disable-json-widget`, `--disable-auto-complete` | integrations & toggles |

Run `./manage.py admin_generator --help` for the full list.

> **Tip:** pairs perfectly with Django's `inspectdb` for
> [legacy databases](https://docs.djangoproject.com/en/stable/howto/legacy-databases/):
> generate the models, then generate the admin.

## Live demo

Spin up a self-documenting blog demo whose `admin.py` is fully auto-generated:

```sh
tox -e demo        # or: uv run --extra demo python test_project/manage.py demo
```

It migrates, seeds realistic data, and opens the admin (login `admin` /
`admin`). The index page explains exactly what was generated and why:

![Self-documenting demo index](https://raw.githubusercontent.com/WoLpH/django-admin-generator/develop/docs/images/admin-index.png)

See [`test_project/README.md`](https://github.com/WoLpH/django-admin-generator/blob/develop/test_project/README.md)
for a guided tour.

## Compatibility

- **Python** 3.10 – 3.13
- **Django** 4.2, 5.0, 5.1, 5.2, 6.0

## Development

This project uses [uv](https://docs.astral.sh/uv/) and [tox](https://tox.wiki/):

```sh
uv sync --extra dev      # create the environment
uv run pytest            # run the tests (100% coverage)
uv run ruff check .      # lint
uv run tox               # full matrix: tests, lint, types, docs
```

## Links

- **Documentation**: <https://django-admin-generator.readthedocs.io/en/latest/>
- **Source**: <https://github.com/WoLpH/django-admin-generator>
- **Bug reports**: <https://github.com/WoLpH/django-admin-generator/issues>
- **PyPI**: <https://pypi.org/project/django-admin-generator/>
- **Blog**: <https://w.wol.ph/>

## License

BSD-3-Clause — see [LICENSE](LICENSE).
