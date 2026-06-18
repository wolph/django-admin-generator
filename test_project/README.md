# Django Admin Generator — live demo

A tiny blog project whose `admin.py` is **entirely auto-generated** by
`django-admin-generator`. Use it to see, in a real Django admin, what the tool
produces and why.

## Launch (one command)

From the repository root:

```sh
uv run --extra demo python test_project/manage.py demo
```

or, if you use tox:

```sh
tox -e demo
```

This migrates the database, seeds realistic sample data (4 authors, 8
categories, 120 tags, 150 posts, ~230 comments), starts the dev server, and
opens your browser. Then log in:

- **URL**: <http://127.0.0.1:8000/admin/>
- **Login**: `admin` / `admin`

The admin index page documents itself — it lists what was generated and links
to each example.

## Guided tour

| Open | What to notice |
| ---- | -------------- |
| **Posts** | `date_hierarchy` drill-down bar (by `created_at`) and `list_filter` for the date / boolean / FK fields. |
| **Add a Post** | Typing the title auto-fills the `slug` (`prepopulated_fields`); `tags` uses an autocomplete widget. |
| **Comments** | `post` uses a `raw_id_fields` lookup popup because Post has >100 rows. |
| **Tags** | No `list_filter` — 120 tags exceed the threshold, so no useless high-cardinality filter is added. |
| **Authors** | `search_fields` on `name`/`slug`; the `bio` TextField is shown but never used as a filter (DISTINCT on text is unsafe on some DBs). |

## Regenerate the admin live

The committed `blog/admin.py` is the (annotated) generator output. Reproduce it
any time:

```sh
# print to stdout
uv run --extra demo python test_project/manage.py admin_generator blog -p slug=title

# overwrite blog/admin.py
uv run --extra demo python test_project/manage.py admin_generator blog -p slug=title --write --force
```

(`-p slug=title` prepopulates Post slugs from the title; the default looks for a
`name` field, which Post does not have.)

`test_project` doubles as the package's test harness, so the models are chosen
to exercise every generator code path.
