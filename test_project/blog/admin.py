"""Annotated output of ``python manage.py admin_generator blog -p slug=title``.

Every option below was chosen *automatically* by django-admin-generator from
the models in ``blog/models.py`` and ``blog/taxonomy/models.py``. The comments
explain the heuristic behind each one. Regenerate the raw (un-annotated)
version any time with::

    python manage.py admin_generator blog -p slug=title --write --force

``-p slug=title`` tells it to prepopulate Post slugs from ``title`` (the
default looks for a ``name`` field, which Post does not have). Imports were
moved to the top here so the file passes ruff; the generator emits them inline,
which is otherwise identical.
"""

from django.contrib import admin

import test_project.blog.models as models
import test_project.blog.taxonomy.models as taxonomy_models

# --- Demo branding (added by hand, not generated) -------------------------
admin.site.site_header = 'Django Admin Generator — Live Demo'
admin.site.site_title = 'admin_generator demo'
admin.site.index_title = 'Auto-generated admin'


class ModelAdminBase(admin.ModelAdmin):
    formfield_overrides = {}


class CategoryAdmin(ModelAdminBase):
    # name/slug -> search_fields + prepopulated_fields (slug auto-fills).
    # Few rows, so every low-cardinality field also becomes a list_filter.
    list_display = ('id', 'name', 'slug')
    list_filter = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ['name']}


class TagAdmin(ModelAdminBase):
    # 120 tags > the list_filter threshold (25), so no list_filter is added —
    # filtering by a high-cardinality field would be useless.
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ['name']}


class AuthorAdmin(ModelAdminBase):
    # bio is a TextField: kept in list_display but excluded from list_filter
    # (DISTINCT on text columns is unsafe on Postgres/Oracle/SQL Server).
    list_display = ('id', 'name', 'slug', 'bio')
    list_filter = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ['name']}


class PostAdmin(ModelAdminBase):
    # created_at/published_at (DateField) + is_published (BooleanField) +
    # author/category (FK with few rows) -> list_filter. body (TextField) is
    # shown but not filtered. tags (M2M) -> autocomplete_fields. slug is
    # prepopulated from title (via -p slug=title). date_hierarchy picks
    # created_at because its name matches the date-hierarchy name list.
    list_display = (
        'id',
        'title',
        'slug',
        'body',
        'created_at',
        'published_at',
        'is_published',
        'author',
        'category',
    )
    list_filter = (
        'created_at',
        'published_at',
        'is_published',
        'author',
        'category',
    )
    autocomplete_fields = ('tags',)
    search_fields = ('slug',)
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'created_at'


class CommentAdmin(ModelAdminBase):
    # post is an FK to Post (150 rows > the 100 raw_id threshold) -> a raw_id
    # lookup popup instead of a huge dropdown. created_at -> date_hierarchy.
    list_display = ('id', 'author_name', 'body', 'post', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('post',)
    date_hierarchy = 'created_at'


def _register(model, admin_class):
    admin.site.register(model, admin_class)


_register(taxonomy_models.Category, CategoryAdmin)
_register(taxonomy_models.Tag, TagAdmin)
_register(models.Author, AuthorAdmin)
_register(models.Post, PostAdmin)
_register(models.Comment, CommentAdmin)
