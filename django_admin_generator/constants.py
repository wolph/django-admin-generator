"""Default thresholds and field-name heuristics for admin generation."""

from __future__ import annotations

import typing

from django.db import models

MAX_LINE_WIDTH: typing.Final[int] = 78
INDENT_WIDTH: typing.Final[int] = 4

#: Field types that are good candidates for ``list_filter``.
LIST_FILTER: typing.Final[
    tuple[type[models.Field[typing.Any, typing.Any]], ...]
] = (
    models.DateField,
    models.DateTimeField,
    models.ForeignKey,
    models.BooleanField,
)

#: Field names that should end up in ``search_fields``.
SEARCH_FIELD_NAMES: typing.Final[tuple[str, ...]] = (
    'name',
    'slug',
)

#: Field names that are good candidates for ``date_hierarchy``.
DATE_HIERARCHY_NAMES: typing.Final[tuple[str, ...]] = (
    'joined_at',
    'updated_at',
    'created_at',
)

#: ``field=other_field`` specs that should end up in ``prepopulated_fields``.
PREPOPULATED_FIELD_NAMES: typing.Final[tuple[str, ...]] = ('slug=name',)

DATE_HIERARCHY_THRESHOLD: typing.Final[int] = 250
LIST_FILTER_THRESHOLD: typing.Final[int] = 25
RAW_ID_THRESHOLD: typing.Final[int] = 100
NO_QUERY_DB: typing.Final[bool] = False
