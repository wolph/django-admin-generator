"""Model introspection and ``admin.py`` source generation."""

from __future__ import annotations

import importlib.util
import re
import typing
from collections.abc import Callable, Iterable, Iterator

from django.apps import AppConfig
from django.db import models
from django.db.models.options import Options
from python_utils import UniqueList

from . import templates
from .constants import (
    DATE_HIERARCHY_NAMES,
    DATE_HIERARCHY_THRESHOLD,
    INDENT_WIDTH,
    LIST_FILTER,
    LIST_FILTER_THRESHOLD,
    MAX_LINE_WIDTH,
    NO_QUERY_DB,
    PREPOPULATED_FIELD_NAMES,
    RAW_ID_THRESHOLD,
    SEARCH_FIELD_NAMES,
)
from .discovery import get_models

if typing.TYPE_CHECKING:
    AnyField = models.Field[typing.Any, typing.Any]


class AdminApp:
    """Render the admin classes for every (matching) model in an app."""

    def __init__(
        self,
        app: AppConfig,
        model_res: list[re.Pattern[str]],
        **options: typing.Any,
    ) -> None:
        self.app: AppConfig = app
        self.model_res: list[re.Pattern[str]] = model_res
        self.options: dict[str, typing.Any] = options
        self._reversion_enabled: bool = False

    def __iter__(self) -> Iterator[AdminModel]:
        for model in get_models(self.app):
            admin_model = AdminModel(model, **self.options)

            for model_re in self.model_res:
                if model_re.search(admin_model.name):
                    break
            else:
                if self.model_res:
                    continue

            yield admin_model

    def __str__(self) -> str:
        return ''.join(self._unicode_generator())

    def _unicode_generator(self) -> Iterator[str]:
        imports: list[str] = []
        formfield_overrides: dict[str, typing.Any] = {}

        self._detect_json_widget_support(formfield_overrides, imports)
        yield from self._yield_imports_and_base_classes(
            imports, formfield_overrides
        )

        models_: dict[str, str] = {}
        modules: dict[str, str] = {}
        module_names: dict[str, str] = {}
        for admin_model in sorted(self, key=lambda x: x.model.__module__):
            model = admin_model.model
            module = model.__module__
            # Use a previously generated module name or the last part of the
            # module path.
            name = modules.get(module, module.rsplit('.', 1)[-1])

            # If the module name was already used, use the last two parts of
            # the module path, converting `project.spam.models` to
            # `spam_models`.
            if module_names.get(name, module) != module:
                name = '_'.join(module.rsplit('.', 2)[-2:])

            # Store the module name and models for later use.
            module_names[name] = module
            modules[module] = name
            models_[admin_model.name] = name

        for module, name in sorted(modules.items()):
            yield f'import {module} as {name}\n'

        admin_model_names: list[str] = []
        for admin_model in self:
            base_class = 'ModelAdminBase'
            if self._reversion_enabled:  # pragma: no cover
                regex = self.options.get('reversion_admin_regex')
                if regex and re.match(regex, admin_model.name):
                    base_class = 'VersionModelAdminBase'

            yield templates.PRINT_ADMIN_CLASS.format(
                name=admin_model.name,
                class_=admin_model,
                base_class=base_class,
            )
            admin_model_names.append(admin_model.name)

        yield templates.PRINT_ADMIN_REGISTRATION_METHOD

        for name in admin_model_names:
            full_name = f'{models_[name]}.{name}'
            context = dict(name=name, full_name=full_name)
            row = templates.PRINT_ADMIN_REGISTRATION.format(**context)
            # Wrap the registration call onto multiple lines when the model
            # name is long enough to exceed the line width.
            if len(row) > MAX_LINE_WIDTH:  # pragma: no cover
                row = templates.PRINT_ADMIN_REGISTRATION_LONG.format(**context)
            yield row

    def _detect_json_widget_support(
        self,
        formfield_overrides: dict[str, typing.Any],
        imports: list[str],
    ) -> None:
        if self.options.get('disable_json_widget'):
            return
        # The body needs the optional django-json-widget package installed.
        available = importlib.util.find_spec('django_json_widget') is not None
        if available:  # pragma: no cover
            self._add_json_widget_imports(formfield_overrides, imports)

    @staticmethod
    def _add_json_widget_imports(
        formfield_overrides: dict[str, typing.Any],
        imports: list[str],
    ) -> None:  # pragma: no cover - requires optional django-json-widget
        imports.append(
            'from django_json_widget.widgets import JSONEditorWidget'
        )
        imports.append('from django.db.models import JSONField')
        formfield_overrides['JSONField'] = {'widget': 'JSONEditorWidget'}

    def _yield_imports_and_base_classes(
        self,
        imports: list[str],
        formfield_overrides: dict[str, typing.Any],
    ) -> Iterator[str]:
        addendum = ''
        enabled = bool(self.options.get('enable_reversion'))
        available = importlib.util.find_spec('reversion') is not None
        if (
            enabled and available
        ):  # pragma: no cover - optional django-reversion
            self._reversion_enabled = True
            addendum = self._build_reversion_addendum(imports)

        yield templates.PRINT_IMPORTS_BASE.format(
            formfield_overrides=formfield_overrides,
            imports='\n'.join(imports),
            model_admin_class=self.options.get('admin_class'),
        )

        yield addendum

    def _build_reversion_addendum(
        self, imports: list[str]
    ) -> str:  # pragma: no cover - requires optional django-reversion
        imports.append(self.options.get('reversion_admin_class_import', ''))
        admin_class = self.options.get('reversion_admin_class')
        assert admin_class != 'VersionModelAdminBase', (
            'The reversion admin base class cannot be the same as '
            'the default admin base class'
        )
        return (
            templates.VERSION_ADMIN_CLASS.format(
                reversion_admin_class=admin_class,
            )
            + '\n\n'
        )

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}[{self.app}]>'


class AdminModel:
    """Introspect a single model and render its ``ModelAdmin`` body."""

    PRINTABLE_PROPERTIES: typing.ClassVar[tuple[str, ...]] = (
        'list_display',
        'list_filter',
        'raw_id_fields',
        'autocomplete_fields',
        'search_fields',
        'prepopulated_fields',
        'date_hierarchy',
    )

    def __init__(
        self,
        model: type[models.Model],
        raw_id_threshold: int = RAW_ID_THRESHOLD,
        date_hierarchy_threshold: int = DATE_HIERARCHY_THRESHOLD,
        list_filter_threshold: int = LIST_FILTER_THRESHOLD,
        search_field_names: tuple[str, ...] = SEARCH_FIELD_NAMES,
        date_hierarchy_names: tuple[str, ...] = DATE_HIERARCHY_NAMES,
        prepopulated_field_names: tuple[str, ...] = PREPOPULATED_FIELD_NAMES,
        no_query_db: bool = NO_QUERY_DB,
        auto_complete: list[str] | None = None,
        disable_auto_complete: bool = False,
        **options: typing.Any,
    ) -> None:
        self.model: type[models.Model] = model
        self.list_display: list[str] = UniqueList()
        self.list_filter: list[str] = UniqueList()
        self.raw_id_fields: list[str] = UniqueList()
        self.search_fields: list[str] = UniqueList()
        self.autocomplete_fields: list[str] = UniqueList()
        self.prepopulated_fields: dict[str, list[str]] = {}
        self.date_hierarchy: str | None = None
        self.search_field_names: tuple[str, ...] = search_field_names
        self.raw_id_threshold: int = raw_id_threshold
        self.list_filter_threshold: int = list_filter_threshold
        self.date_hierarchy_threshold: int = date_hierarchy_threshold
        self.date_hierarchy_names: tuple[str, ...] = date_hierarchy_names
        self.prepopulated_field_names: tuple[str, ...] = (
            prepopulated_field_names
        )
        self.query_db: bool = not no_query_db
        # An explicit (possibly empty) `auto_complete` list takes precedence;
        # only fall back to the on/off default when it was not provided.
        self.auto_complete: list[str] | bool
        if disable_auto_complete:
            self.auto_complete = False
        elif auto_complete is not None:
            self.auto_complete = auto_complete
        else:
            self.auto_complete = True
        self.processed: bool = False

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}[{self.name}]>'

    @property
    def name(self) -> str:
        return self.model.__name__

    def _process_many_to_many(
        self, meta: Options[models.Model]
    ) -> Iterator[str]:
        raw_id_threshold = self.raw_id_threshold
        for field in meta.local_many_to_many:
            if field.name in self.autocomplete_fields:
                continue

            related_model = self._get_related_model(field)
            related_objects = related_model._default_manager.all()
            if related_objects[:raw_id_threshold].count() < raw_id_threshold:
                yield field.name

    def _process_many_to_many_autocomplete(
        self, meta: Options[models.Model]
    ) -> Iterator[str]:
        auto_complete = self.auto_complete
        for field in meta.local_many_to_many:
            if auto_complete is True or (
                isinstance(auto_complete, list) and field.name in auto_complete
            ):
                yield field.name

    def _process_fields(self, meta: Options[models.Model]) -> Iterator[str]:
        parent_fields = meta.parents.values()
        for field in meta.fields:
            name = self._process_field(field, parent_fields)
            if name:  # pragma: no cover
                yield name

    @classmethod
    def _get_related_model(cls, field: AnyField) -> type[models.Model]:
        return typing.cast(
            'type[models.Model]',
            field.remote_field.model,  # type: ignore[union-attr]
        )

    def _process_foreign_key(self, field: AnyField) -> None:
        raw_id_threshold = self.raw_id_threshold
        list_filter_threshold = self.list_filter_threshold
        max_count = max(list_filter_threshold, raw_id_threshold)
        related_model = self._get_related_model(field)
        related_qs = related_model._default_manager.all()
        related_count = related_qs[:max_count].count()

        if related_count >= raw_id_threshold:
            self.raw_id_fields.append(field.name)

        elif related_count < list_filter_threshold:
            self.list_filter.append(field.name)

        else:  # pragma: no cover
            pass  # Do nothing :)

    def _process_field(
        self,
        field: AnyField,
        parent_fields: Iterable[AnyField | None],
    ) -> str | None:
        if field in parent_fields:  # pragma: no cover
            return None

        self.list_display.append(field.name)
        if isinstance(field, LIST_FILTER):
            if isinstance(field, models.ForeignKey) and self.query_db:
                self._process_foreign_key(field)
            else:
                self.list_filter.append(field.name)

        if field.name in self.search_field_names:
            self.search_fields.append(field.name)

        return field.name

    def __str__(self) -> str:
        return ''.join(self._unicode_generator())

    def _yield_value(self, key: str, value: object) -> str:
        if isinstance(value, (list, set, tuple)):
            return self._yield_tuple(key, tuple(value))
        elif isinstance(value, dict):
            return self._yield_dict(key, value)
        elif isinstance(value, str):
            return self._yield_string(key, value)
        else:  # pragma: no cover
            raise TypeError(f'{type(value)} is not supported in {value!r}')

    def _yield_string(
        self,
        key: str,
        value: object,
        converter: Callable[[typing.Any], str] = repr,
    ) -> str:
        return templates.PRINT_ADMIN_PROPERTY.format(
            key=key,
            value=converter(value),
        )

    def _yield_dict(
        self, key: str, value: dict[typing.Any, typing.Any]
    ) -> str:
        row_parts: list[str] = []
        row = self._yield_string(key, value)
        if len(row) > MAX_LINE_WIDTH:
            row_parts.append(self._yield_string(key, '{', str))
            indent = 2 * INDENT_WIDTH * ' '
            row_parts.extend(f'{indent}{k!r}: {v!r}' for k, v in value.items())
            row_parts.append(INDENT_WIDTH * ' ' + '}')
            row = '\n'.join(row_parts)

        return row

    def _yield_tuple(self, key: str, value: tuple[typing.Any, ...]) -> str:
        row_parts: list[str] = []
        row = self._yield_string(key, value)
        if len(row) > MAX_LINE_WIDTH:
            row_parts.append(self._yield_string(key, '(', str))
            indent = 2 * INDENT_WIDTH * ' '
            row_parts.extend(f'{indent}{v!r},' for v in value)
            row_parts.append(INDENT_WIDTH * ' ' + ')')
            row = '\n'.join(row_parts)

        return row

    def _unicode_generator(self) -> Iterator[str]:
        self._process()
        for key in self.PRINTABLE_PROPERTIES:
            value = getattr(self, key)
            if value:
                yield self._yield_value(key, value)

    def _process(self) -> None:
        meta = self.model._meta
        qs = self.model._default_manager.all()

        # Use `append` rather than `+=`: UniqueList tracks membership in a
        # separate set that `list.__iadd__` would bypass, which would break
        # the `field.name in self.autocomplete_fields` check below.
        if self.auto_complete:
            for field_name in self._process_many_to_many_autocomplete(meta):
                self.autocomplete_fields.append(field_name)
        if self.query_db:
            for field_name in self._process_many_to_many(meta):
                self.raw_id_fields.append(field_name)

        field_names = list(self._process_fields(meta))

        if self.query_db:
            self._collect_list_filter(qs, field_names)
            self._collect_date_hierarchy(qs, field_names)

        self._collect_prepopulated_fields(field_names)

        self.processed = True

    #: Field types that do not support ``DISTINCT`` on some databases
    #: (PostgreSQL, Oracle, SQL Server) and must be kept out of the
    #: ``distinct()`` queries used to populate ``list_filter``.
    NON_DISTINCT_FIELDS: typing.ClassVar[tuple[type[AnyField], ...]] = (
        models.TextField,
        models.JSONField,
        models.BinaryField,
        models.FileField,
    )

    def _collect_list_filter(
        self, qs: models.QuerySet[models.Model], field_names: list[str]
    ) -> None:
        threshold = self.list_filter_threshold + 1
        for field in field_names:
            if isinstance(
                self.model._meta.get_field(field), self.NON_DISTINCT_FIELDS
            ):
                continue
            distinct_count = len(qs.only(field).distinct()[:threshold])
            if distinct_count <= self.list_filter_threshold:
                self.list_filter.append(field)

    def _collect_date_hierarchy(
        self, qs: models.QuerySet[models.Model], field_names: list[str]
    ) -> None:
        if qs.count() >= self.date_hierarchy_threshold:
            return
        for field_name in self.date_hierarchy_names[::-1]:
            if field_name in field_names and not self.date_hierarchy:
                self.date_hierarchy = field_name
                break

    def _collect_prepopulated_fields(self, field_names: list[str]) -> None:
        for spec in sorted(self.prepopulated_field_names):
            key, values_raw = spec.split('=', 1)
            values = values_raw.split(',')
            if key not in field_names:
                continue
            if all(value in field_names for value in values):
                self.prepopulated_fields[key] = values
