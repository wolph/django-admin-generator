What the generator decides
==========================

The generator reads ``Model._meta``, counts a few rows, and fills in seven
``ModelAdmin`` attributes. Knowing which rule produced a line tells you which
flag to reach for when you disagree with it.

Attributes it fills in
----------------------

``list_display``
    Every local field on the model, in declaration order, with fields
    inherited through a parent link left out.

``list_filter``
    Fields that make sense as a sidebar filter. See `Filters and raw ids`_.

``raw_id_fields``
    Relations with too many rows to render as a select box.

``autocomplete_fields``
    Many-to-many relations, which the admin renders as a search box rather
    than a multi-select list.

``search_fields``
    Fields whose name appears in the search field names, ``name`` and ``slug``
    by default. Extend the list with ``-s``.

``prepopulated_fields``
    Pairs like ``slug=name``, emitted when both fields exist on the model.
    Extend with ``-p``.

``date_hierarchy``
    A single date field for the drill-down navigation above the changelist.

Filters and raw ids
-------------------

Four field types are filter candidates from their type alone:
:class:`~django.db.models.DateField`,
:class:`~django.db.models.DateTimeField`,
:class:`~django.db.models.BooleanField` and
:class:`~django.db.models.ForeignKey`.

A foreign key is the interesting case, because a select box listing fifty
thousand related rows is worse than no widget at all. The generator counts the
related table and sorts the key into one of three outcomes:

.. list-table::
    :header-rows: 1
    :widths: 40 60

    * - Related rows
      - Outcome
    * - Fewer than ``--list-filter-threshold`` (25)
      - ``list_filter``
    * - At or above ``--raw-id-threshold`` (100)
      - ``raw_id_fields``
    * - Between the two
      - Neither, because it is too big to filter on and small enough to pick
        from a list

Any other field also becomes a filter when it has few enough distinct values.
The generator runs a bounded ``DISTINCT`` query per field and keeps the field
when the count stays at or below the list filter threshold. Text, JSON, binary
and file fields are skipped, because ``DISTINCT`` on those columns fails on
PostgreSQL, Oracle and SQL Server.

Date hierarchies
----------------

A date hierarchy is cheap on a small table and slow on a large one, so the
generator only emits one when the model holds fewer rows than
``--date-hierarchy-threshold`` (250). It then takes the first name that
matches, preferring ``created_at``, then ``updated_at``, then ``joined_at``.

Extend the candidates rather than renaming your fields:

.. code-block:: console

    ./manage.py admin_generator blog -d published_at

Many-to-many relations
----------------------

Every many-to-many relation becomes an ``autocomplete_fields`` entry by
default. Autocomplete needs ``search_fields`` on the related model's admin, so
generate the related app too rather than only the one you started with.

Narrow it to specific fields, or turn it off entirely:

.. code-block:: console

    ./manage.py admin_generator blog --auto-complete tags
    ./manage.py admin_generator blog --disable-auto-complete

With autocomplete off, a many-to-many relation may be emitted as a raw id
field instead, which keeps the change form usable without a search endpoint.

Running without a database
--------------------------

Row counts drive the filter, raw id and date hierarchy decisions, so all three
change shape when you pass ``-n``:

.. code-block:: console

    ./manage.py admin_generator blog --no-query-db

Every type-based filter candidate then becomes a ``list_filter`` entry, no
field is promoted to ``raw_id_fields`` on size, and no ``date_hierarchy`` is
emitted. This is the mode for a machine with no database access, and for a
development database whose row counts say nothing about production.

.. note::

    The counts come from whichever database the command connects to. Running
    against a nearly empty development copy is what produces a select box that
    turns into a thirty thousand row dropdown once deployed.
