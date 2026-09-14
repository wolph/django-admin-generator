:tocdepth: 2

.. raw:: html

    <nav class="dag-links" aria-label="Project links">
      <a href="https://pypi.org/project/django-admin-generator/">PyPI</a>
      <a href="https://github.com/WoLpH/django-admin-generator">Source code</a>
      <a href="https://github.com/WoLpH/django-admin-generator/issues">Issues</a>
    </nav>
    <p class="dag-eyebrow">Django admin scaffolding</p>

Stop hand-writing admin.py
==========================

.. container:: dag-hero

    A management command that reads your models and prints a complete
    ``admin.py``: list displays, filters, search fields, raw id fields, date
    hierarchies, prepopulated slugs and autocompletes. You review the output
    and keep what you want.

    .. raw:: html

        <div class="dag-actions">
          <a class="dag-button" href="quickstart.html">Get started <span aria-hidden="true">&rarr;</span></a>
          <a class="dag-button dag-button-secondary" href="heuristics.html">See what it generates</a>
        </div>

Generate an admin in one command
--------------------------------

Install the package on Python 3.10 or later and add it to ``INSTALLED_APPS``:

.. code-block:: console

    python -m pip install django-admin-generator

Point the command at an app and read the result:

.. code-block:: console

    ./manage.py admin_generator blog

.. code-block:: python

    class PostAdmin(ModelAdminBase):
        list_display = ('id', 'title', 'author', 'category', 'is_published')
        list_filter = ('created_at', 'published_at', 'is_published', 'author')
        autocomplete_fields = ('tags',)
        search_fields = ('slug',)
        prepopulated_fields = {'slug': ['title']}
        date_hierarchy = 'created_at'

Nothing is written to disk until you ask for it, so the first run is always
safe. Add ``--write`` once the output looks right.

.. image:: images/changelist.png
    :alt: A generated changelist with columns, a filter sidebar and a date drill-down

The changelist above, filter sidebar and date drill-down included, came from
that single command with no hand-written admin code.

Pick your next step
-------------------

.. raw:: html

    <div class="dag-cards">
      <a class="dag-card" href="quickstart.html">
        <h3>Quickstart</h3>
        <p>Install, generate, review, and write the file into your app.</p>
        <span>Five minute tour <span aria-hidden="true">&rarr;</span></span>
      </a>
      <a class="dag-card" href="heuristics.html">
        <h3>What it decides</h3>
        <p>Which fields become filters, raw ids or autocompletes, and why.</p>
        <span>Tuning guide <span aria-hidden="true">&rarr;</span></span>
      </a>
      <a class="dag-card" href="usage.html">
        <h3>Command reference</h3>
        <p>Every flag the management command accepts, grouped by job.</p>
        <span>All options <span aria-hidden="true">&rarr;</span></span>
      </a>
    </div>

.. note::

    The generator inspects your models and, unless you pass ``--no-query-db``,
    counts rows to decide between a dropdown filter and a raw id field. Point
    it at a database that resembles production if you want those counts to be
    meaningful.

.. raw:: html

    <nav class="dag-footer-links" aria-label="More documentation">
      <a href="api/index.html">API reference</a>
      <a href="demo.html">Live demo</a>
      <a href="sponsor.html">Support this project</a>
      <a href="https://github.com/WoLpH/django-admin-generator/issues">Report an issue</a>
    </nav>

.. toctree::
    :hidden:
    :caption: Get started

    quickstart
    usage

.. toctree::
    :hidden:
    :caption: Guides

    heuristics
    integrations
    demo

.. toctree::
    :hidden:
    :caption: Reference

    api/index
    license

.. toctree::
    :hidden:
    :caption: Project

    sponsor
