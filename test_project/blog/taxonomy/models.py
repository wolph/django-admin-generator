"""Taxonomy models for the blog demo.

These live in a *second* ``models`` module (``blog.taxonomy.models``)
alongside ``blog.models``. The generator notices the two modules share the
short name ``models`` and disambiguates the imports it writes
(``import ... as taxonomy_models``) — a small feature worth showing off.
"""

from django.db import models


class Category(models.Model):
    """A broad post category.

    ``name`` + ``slug`` make the generator add ``search_fields`` and
    ``prepopulated_fields``. As an FK target with only a handful of rows it
    becomes a ``list_filter`` on ``Post``.
    """

    name = models.CharField(
        max_length=100,
        help_text='Appears in list_display and drives search_fields.',
    )
    slug = models.SlugField(
        max_length=100,
        help_text='Auto-prepopulated from name in the generated admin.',
    )

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """A free-form label.

    The demo seeds well over 100 tags, so the generator turns ``Post.tags``
    into ``raw_id_fields`` (a lookup popup) rather than a giant multi-select.
    """

    name = models.CharField(max_length=50, help_text='Drives search_fields.')
    slug = models.SlugField(
        max_length=50,
        help_text='Auto-prepopulated from name.',
    )

    def __str__(self) -> str:
        return self.name
