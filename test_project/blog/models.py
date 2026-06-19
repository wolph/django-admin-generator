"""Blog demo models.

Each field is chosen to trigger a specific Django Admin Generator heuristic —
see the ``help_text`` on each and the generated ``blog/admin.py`` for the
mapping. The taxonomy models (``Category``, ``Tag``) are imported here so they
register under the ``blog`` app while living in their own ``models`` module.
"""

from django.db import models

from .taxonomy.models import Category, Tag

__all__ = ['Author', 'Category', 'Comment', 'Post', 'Tag']


class Author(models.Model):
    """A post author.

    ``name``/``slug`` → ``search_fields`` + ``prepopulated_fields``; ``bio`` is
    a TextField, which the generator keeps out of ``list_filter`` (DISTINCT on
    text columns is unsafe on several databases).
    """

    name = models.CharField(max_length=100, help_text='search_fields.')
    slug = models.SlugField(
        max_length=100, help_text='prepopulated from name.'
    )
    bio = models.TextField(
        blank=True, help_text='TextField: skipped by list_filter.'
    )

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    """A blog post — the showcase model.

    ``author``/``category`` are FKs with few rows → ``list_filter``;
    ``tags`` is M2M → autocomplete (or raw_id when large); ``published_at`` is
    a DateField → ``date_hierarchy`` + ``list_filter``; ``is_published`` is a
    BooleanField → ``list_filter``; ``title``/``slug`` → search + prepopulate.
    """

    title = models.CharField(max_length=200, help_text='list_display.')
    slug = models.SlugField(
        max_length=200, help_text='prepopulated from title.'
    )
    body = models.TextField(help_text='TextField: skipped by list_filter.')
    created_at = models.DateField(
        help_text="DateField named 'created_at': becomes date_hierarchy.",
    )
    published_at = models.DateField(
        help_text='DateField: list_filter (not date_hierarchy by name).'
    )
    is_published = models.BooleanField(
        default=False, help_text='BooleanField: list_filter.'
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        help_text='FK with few rows: becomes a list_filter.',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        help_text='FK with few rows: becomes a list_filter.',
    )
    tags = models.ManyToManyField(
        Tag, help_text='M2M: autocomplete, or raw_id when there are many tags.'
    )

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """A comment on a post.

    ``post`` is an FK to a model with many rows → ``raw_id_fields``;
    ``created_at`` is a DateField → ``date_hierarchy`` + ``list_filter``.
    """

    author_name = models.CharField(
        max_length=100, help_text='search? no (not name/slug).'
    )
    body = models.TextField(help_text='TextField: skipped by list_filter.')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        help_text='FK to a large table: becomes raw_id_fields.',
    )
    created_at = models.DateField(
        help_text='DateField: date_hierarchy + list_filter.'
    )

    def __str__(self) -> str:
        return f'Comment by {self.author_name}'
