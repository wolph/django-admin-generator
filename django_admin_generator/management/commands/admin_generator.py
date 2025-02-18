import pathlib
import re
import sys
from pathlib import Path
from typing import Any, List

import python_utils
import six
from django.apps import AppConfig
from django.apps.registry import apps
from django.conf import settings
from django.db import models
from django_utils.management.commands import base_command
from python_utils import logger, types


def get_models(app):
    for model in app.get_models():
        yield model


def get_apps() -> types.Generator[types.Tuple[str, AppConfig], None, None]:
    for app_config in apps.get_app_configs():
        yield app_config.name, app_config
        yield app_config.name.rsplit('.')[-1], app_config


def get_local_apps() -> List[AppConfig]:
    local_app_configs: List[AppConfig] = []
    # Get the absolute path of the project's base directory as a Path object
    project_root: Path = Path(settings.BASE_DIR).resolve()

    # If your virtual environment is inside the project directory, get its path
    venv_path: Path = project_root / 'venv'  # Adjust 'venv' if your virtualenv folder has a different name

    for app_config in apps.get_app_configs():
        app_path: Path = Path(app_config.path).resolve()
        # Check if the app is within the project directory but not in the virtual environment or site-packages
        if (project_root in app_path.parents or app_path == project_root) \
                and (venv_path not in app_path.parents) \
                and ('site-packages' not in str(app_path)):
            local_app_configs.append(app_config)
    return local_app_configs


MAX_LINE_WIDTH = 78
INDENT_WIDTH = 4

LIST_FILTER = (
    models.DateField,
    models.DateTimeField,
    models.ForeignKey,
    models.BooleanField,
)

SEARCH_FIELD_NAMES = (
    'name',
    'slug',
)

DATE_HIERARCHY_NAMES = (
    'joined_at',
    'updated_at',
    'created_at',
)

PREPOPULATED_FIELD_NAMES = (
    'slug=name',
)

DATE_HIERARCHY_THRESHOLD = 250
LIST_FILTER_THRESHOLD = 25
RAW_ID_THRESHOLD = 100
NO_QUERY_DB = False

PRINT_IMPORTS_BASE = '''
from django.contrib import admin
{imports}

class ModelAdminBase({model_admin_class}):
    formfield_overrides = {formfield_overrides}
'''

VERSION_ADMIN_CLASS = '''
class VersionModelAdminBase({reversion_admin_class}, ModelAdminBase):
    pass
'''

PRINT_ADMIN_CLASS = '''

class %(name)sAdmin(%(base_class)s):
%(class_)s
'''

PRINT_ADMIN_REGISTRATION_METHOD = '''

def _register(model, admin_class):
    admin.site.register(model, admin_class)

'''

PRINT_ADMIN_REGISTRATION = '''
_register(%(full_name)s, %(name)sAdmin)'''

PRINT_ADMIN_REGISTRATION_LONG = '''
_register(
    %(full_name)s,
    %(name)sAdmin)'''

PRINT_ADMIN_PROPERTY = '''
    %(key)s = %(value)s'''


class AdminApp:
    def __init__(self, app, model_res, **options):
        self.app = app
        self.model_res = model_res
        self.options = options
        self._reversion_enabled = False

    def __iter__(self):
        for model in get_models(self.app):
            admin_model = AdminModel(model, **self.options)

            for model_re in self.model_res:
                if model_re.search(admin_model.name):
                    break
            else:
                if self.model_res:
                    continue

            yield admin_model

    def __unicode__(self):
        return six.u('').join(self._unicode_generator())

    def __str__(self):  # pragma: no cover
        if six.PY2:
            return six.text_type(self).encode('utf-8', 'replace')
        else:
            return self.__unicode__()

    def _get_imports(self):
        imports = []
        formfield_overrides = dict()
        self._detect_json_widget_support(formfield_overrides, imports)
        return imports, formfield_overrides

    def _unicode_generator(self):
        imports = []
        formfield_overrides = dict()

        self._detect_json_widget_support(formfield_overrides, imports)
        yield from self._yield_imports_and_base_classes(imports, formfield_overrides)

        models = dict()
        modules = dict()
        module_names = dict()
        for admin_model in sorted(self, key=lambda x: x.model.__module__):
            model = admin_model.model
            module = model.__module__
            # Get the module name if it was generated before or use the last
            # part of the module path
            name = modules.get(module, module.rsplit('.', 1)[-1])

            # If the module name was already used, use the last two parts of
            # the module path converting `project.spam.models` to `spam_models`
            if module_names.get(name, module) != module:
                name = '_'.join(module.rsplit('.', 2)[-2:])

            # Store the module name and models for later use.
            module_names[name] = module
            modules[module] = name
            models[admin_model.name] = name

        for module, name in sorted(modules.items()):
            yield 'import %s as %s\n' % (module, name)

        admin_model_names = []
        for admin_model in self:
            if self._reversion_enabled and re.match(self.options.get('reversion_admin_regex'), admin_model.name):
                base_class = 'VersionModelAdminBase'
            else:
                base_class = 'ModelAdminBase'

            yield PRINT_ADMIN_CLASS % dict(
                name=admin_model.name,
                class_=admin_model,
                base_class=base_class,
            )
            admin_model_names.append(admin_model.name)

        yield PRINT_ADMIN_REGISTRATION_METHOD

        for name in admin_model_names:
            full_name = '%s.%s' % (models[name], name)
            context = dict(name=name, full_name=full_name)
            row = PRINT_ADMIN_REGISTRATION % context
            if len(row) > MAX_LINE_WIDTH:
                row = PRINT_ADMIN_REGISTRATION_LONG % context
            yield row

    def _detect_json_widget_support(self, formfield_overrides, imports):
        if not self.options.get('disable_json_widget'):
            try:
                import django_json_widget
            except ImportError:
                pass
            else:
                imports.append(
                    'from django_json_widget.widgets import JSONEditorWidget')
                imports.append('from django.db.models import JSONField')
                formfield_overrides['JSONField'] = {
                    'widget': 'JSONEditorWidget',
                }

    def _yield_imports_and_base_classes(self, imports, formfield_overrides):
        addendum = ''
        if self.options.get('enable_reversion'):
            try:
                import reversion
            except ImportError:
                pass
            else:
                self._reversion_enabled = True
                imports.append(self.options.get('reversion_admin_class_import'))

                assert 'VersionModelAdminBase' != self.options.get('reversion_admin_class'), \
                    'The reversion admin base class cannot be the same as the default admin base class'
                addendum = VERSION_ADMIN_CLASS.format(
                    reversion_admin_class=self.options.get('reversion_admin_class'),
                ) + '\n\n'

        yield PRINT_IMPORTS_BASE.format(
            formfield_overrides=formfield_overrides,
            imports='\n'.join(imports),
            model_admin_class=self.options.get('admin_class'),
        )

        yield addendum

    def __repr__(self):
        return '<%s[%s]>' % (
            self.__class__.__name__,
            self.app,
        )


class AdminModel(object):
    PRINTABLE_PROPERTIES = (
        'list_display',
        'list_filter',
        'raw_id_fields',
        'auto_complete_fields',
        'search_fields',
        'prepopulated_fields',
        'date_hierarchy',
    )

    def __init__(
        self, model, raw_id_threshold=RAW_ID_THRESHOLD,
        date_hierarchy_threshold=DATE_HIERARCHY_THRESHOLD,
        list_filter_threshold=LIST_FILTER_THRESHOLD,
        search_field_names=SEARCH_FIELD_NAMES,
        date_hierarchy_names=DATE_HIERARCHY_NAMES,
        prepopulated_field_names=PREPOPULATED_FIELD_NAMES,
        no_query_db=NO_QUERY_DB,
        auto_complete: list[str] | None=None,
        disable_auto_complete: bool=False,
        **options
    ):
        self.model = model
        self.list_display = python_utils.UniqueList()
        self.list_filter = python_utils.UniqueList()
        self.raw_id_fields = python_utils.UniqueList()
        self.search_fields = python_utils.UniqueList()
        self.auto_complete_fields = python_utils.UniqueList()
        self.prepopulated_fields = {}
        self.date_hierarchy = None
        self.search_field_names = search_field_names
        self.raw_id_threshold = raw_id_threshold
        self.list_filter_threshold = list_filter_threshold
        self.date_hierarchy_threshold = date_hierarchy_threshold
        self.date_hierarchy_names = date_hierarchy_names
        self.prepopulated_field_names = prepopulated_field_names
        self.query_db = not no_query_db
        self.auto_complete = auto_complete or not disable_auto_complete

    def __repr__(self):
        return '<%s[%s]>' % (
            self.__class__.__name__,
            self.name,
        )

    @property
    def name(self):
        return self.model.__name__

    def _process_many_to_many(self, meta):
        raw_id_threshold = self.raw_id_threshold
        for field in meta.local_many_to_many:
            if field.name in self.auto_complete_fields:
                continue

            related_model = self._get_related_model(field)
            related_objects = related_model.objects.all()
            if (related_objects[:raw_id_threshold].count() < raw_id_threshold):
                yield field.name

    def _process_many_to_many_autocomplete(self, meta):
        for field in meta.local_many_to_many:
            if self.auto_complete is True or field.name in self.auto_complete:
                yield field.name

    def _process_fields(self, meta):
        parent_fields = meta.parents.values()
        for field in meta.fields:
            name = self._process_field(field, parent_fields)
            if name:  # pragma: no cover
                yield name

    @classmethod
    def _get_related_model(cls, field):  # pragma: no cover
        if hasattr(field, 'remote_field'):
            related_model = field.remote_field.model
        elif hasattr(field.related, 'related_model'):
            related_model = field.related.related_model
        else:
            related_model = field.related.model

        return related_model

    def _process_foreign_key(self, field):
        raw_id_threshold = self.raw_id_threshold
        list_filter_threshold = self.list_filter_threshold
        max_count = max(list_filter_threshold, raw_id_threshold)
        related_model = self._get_related_model(field)
        related_count = related_model.objects.all()
        related_count = related_count[:max_count].count()

        if related_count >= raw_id_threshold:
            self.raw_id_fields.append(field.name)

        elif related_count < list_filter_threshold:
            self.list_filter.append(field.name)

        else:  # pragma: no cover
            pass  # Do nothing :)

    def _process_field(self, field, parent_fields):
        if field in parent_fields:  # pragma: no cover
            return

        self.list_display.append(field.name)
        if isinstance(field, LIST_FILTER):
            if isinstance(field, models.ForeignKey) and self.query_db:
                self._process_foreign_key(field)
            else:
                self.list_filter.append(field.name)

        if field.name in self.search_field_names:
            self.search_fields.append(field.name)

        return field.name

    def __str__(self):  # pragma: no cover
        if six.PY2:
            return six.text_type(self).encode('utf-8', 'replace')
        else:
            return self.__unicode__()

    def __unicode__(self):
        return six.u('').join(self._unicode_generator())

    def _yield_value(self, key, value):
        if isinstance(value, (list, set, tuple)):
            return self._yield_tuple(key, tuple(value))
        elif isinstance(value, dict):
            return self._yield_dict(key, value)
        elif isinstance(value, six.string_types):
            return self._yield_string(key, value)
        else:  # pragma: no cover
            raise TypeError('%s is not supported in %r' % (type(value), value))

    def _yield_string(self, key, value, converter=repr):
        return PRINT_ADMIN_PROPERTY % dict(
            key=key,
            value=converter(value),
        )

    def _yield_dict(self, key, value):
        row_parts = []
        row = self._yield_string(key, value)
        if len(row) > MAX_LINE_WIDTH:
            row_parts.append(self._yield_string(key, '{', str))
            for k, v in six.iteritems(value):
                row_parts.append('%s%r: %r' % (2 * INDENT_WIDTH * ' ', k, v))

            row_parts.append(INDENT_WIDTH * ' ' + '}')
            row = six.u('\n').join(row_parts)

        return row

    def _yield_tuple(self, key, value):
        row_parts = []
        row = self._yield_string(key, value)
        if len(row) > MAX_LINE_WIDTH:
            row_parts.append(self._yield_string(key, '(', str))
            for v in value:
                row_parts.append(2 * INDENT_WIDTH * ' ' + repr(v) + ',')

            row_parts.append(INDENT_WIDTH * ' ' + ')')
            row = six.u('\n').join(row_parts)

        return row

    def _unicode_generator(self):
        self._process()
        for key in self.PRINTABLE_PROPERTIES:
            value = getattr(self, key)
            if value:
                yield self._yield_value(key, value)

    def _process(self):
        meta = self.model._meta
        qs = self.model.objects.all()

        if self.auto_complete:
            self.auto_complete_fields += list(self._process_many_to_many_autocomplete(meta))
        if self.query_db:
            self.raw_id_fields += list(self._process_many_to_many(meta))

        field_names = list(self._process_fields(meta))

        if self.query_db:
            threshold = self.list_filter_threshold + 1
            for field in field_names:
                distinct_count = len(qs.only(field).distinct()[:threshold])
                if distinct_count <= self.list_filter_threshold:
                    self.list_filter.append(field)

        if self.query_db:
            if qs.count() < self.date_hierarchy_threshold:
                for field_name in self.date_hierarchy_names[::-1]:
                    if field_name in field_names and not self.date_hierarchy:
                        self.date_hierarchy = field_name
                        break

        for k in sorted(self.prepopulated_field_names):
            k, vs = k.split('=', 1)
            vs = vs.split(',')
            if k in field_names:
                incomplete = False
                for v in vs:
                    if v not in field_names:
                        incomplete = True
                        break

                if not incomplete:
                    self.prepopulated_fields[k] = vs

        self.processed = True


class Command(base_command.CustomBaseCommand):
    help = '''Generate a `admin.py` file for the given app (models)'''
    can_import_settings = True
    requires_system_checks = '__all__',

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument(
            '-s', '--search-field', action='append',
            default=SEARCH_FIELD_NAMES,
            help='Fields named like this will be added to `search_fields`'
        )
        parser.add_argument(
            '-d', '--date-hierarchy', action='append',
            default=DATE_HIERARCHY_NAMES,
            help='A field named like this will be set as `date_hierarchy`'
        )
        parser.add_argument(
            '--date-hierarchy-threshold', type=int,
            default=DATE_HIERARCHY_THRESHOLD,
            metavar='DATE_HIERARCHY_THRESHOLD',
            help='If a model has less than DATE_HIERARCHY_THRESHOLD items '
                 'it will be added to `date_hierarchy`'
        )
        parser.add_argument(
            '-p', '--prepopulated-fields', action='append',
            default=PREPOPULATED_FIELD_NAMES,
            help='These fields will be prepopulated by the other field.'
                 'The field names can be specified like `spam=eggA,eggB,eggC`'
        )
        parser.add_argument(
            '-l', '--list-filter-threshold', type=int,
            default=LIST_FILTER_THRESHOLD, metavar='LIST_FILTER_THRESHOLD',
            help='If a foreign key/field has less than LIST_FILTER_THRESHOLD '
                 'items it will be added to `list_filter`'
        )
        parser.add_argument(
            '-r', '--raw-id-threshold', type=int,
            default=RAW_ID_THRESHOLD, metavar='RAW_ID_THRESHOLD',
            help='If a foreign key has more than RAW_ID_THRESHOLD items '
                 'it will be added to `list_filter`'
        )
        parser.add_argument(
            '-n', '--no-query-db', action="store_true", dest='no_query_db',
            help='Don\'t query the database in order to decide whether '
                 'fields/relationships are added to `list_filter`'
        )
        parser.add_argument(
            '-w', '--write', action='store_true',
            help='Write the output to the admin.py file(s)',
        )
        parser.add_argument(
            '-o', '--output', default='admin.py',
            help='Output file name',
        )
        parser.add_argument(
            '-f', '--force', action='store_true',
            help='Overwrite the output file if it exists',
        )
        parser.add_argument(
            '-a', '--append', action='store_true',
            help='Append the output to the output file if it exists',
        )
        parser.add_argument(
            'app',
            help='App to generate admin definitions for, use `all` to generate '
                 'for all local (i.e. not in site-packages) apps'
        )
        parser.add_argument(
            'models', nargs='*',
            help='Regular expressions to filter the models by'
        )
        parser.add_argument(
            '--disable-json-widget', action='store_true',
            help='Disable the JSON widget import and formfield override',
        )
        parser.add_argument(
            '--enable-reversion', action='store_true',
            help='Enable django-reversion support',
        )
        parser.add_argument(
            '--reversion-admin-regex', default=r'.*',
            help='Regular expression to filter the models by for reversion',
        )
        parser.add_argument(
            '--reversion-admin-class', default='VersionAdmin',
            help='The base class for the ModelAdmin classes for reversion',
        )
        parser.add_argument(
            '--reversion-admin-class-import', default='from reversion.admin import VersionAdmin',
            help='The import statement for the base class for the ModelAdmin classes for reversion',
        )
        parser.add_argument(
            '--admin-class', default='admin.ModelAdmin',
            help='The base class for the ModelAdmin classes',
        )
        parser.add_argument(
            '--admin-class-import', default='',
            help='The import statement for the base class for the ModelAdmin classes if it is not the Django default',
        )
        parser.add_argument(
            '--disable-auto-complete', action='store_true',
            help='Disable the auto-complete feature for the many-to-many fields',
        )
        parser.add_argument(
            '--auto-complete', action='append',
            help='Enable the auto-complete feature only for the specified many-to-many fields',
        )

    @classmethod
    def warning(
            cls,
            msg: object,
            *args: object,
            exc_info: logger._ExcInfoType = None,
            stack_info: bool = False,
            stacklevel: int = 1,
            extra: types.Union[types.Mapping[str, object], None] = None,
    ) -> None:
        # This replaces the regular warning method from the CustomBaseCommand
        # since some Django installations capture all logging output
        # unfortunately
        sys.stderr.write(str(msg))
        sys.stderr.write('\n')

    def handle(self, app: types.Optional[str]=None, *args, **kwargs):
        super(Command, self).handle(*args, **kwargs)

        if app == 'all':
            for app in get_local_apps():
                self.handle_app(app, [], **kwargs)
        else:
            installed_apps: dict[str, Any] = dict(get_apps())

            app = installed_apps.get(app)
            if not app:
                self.warning(
                    'This command requires an existing app name as '
                    'argument'
                )
                self.warning('Available apps:')
                for app in sorted(installed_apps):
                    self.warning('    %s' % app)
                sys.exit(1)

            model_res = []
            for model in kwargs.get('models', []):
                model_res.append(re.compile(model, re.IGNORECASE))

            self.handle_app(app, model_res, **kwargs)

    def handle_app(
            self,
            app,
            model_res,
            write: bool=False,
            output: types.Optional[str]=None,
            force: bool=False,
            append: bool=False,
            **options,
    ):
        if output:
            if '/' in output or '\\' in output:
                output_path = pathlib.Path(output)
            else:
                output_path = pathlib.Path(app.path) / output

            print(f'Writing {app.name} to {output_path}', file=sys.stderr)

            if output_path.exists():
                if not force and not append:
                    self.warning(
                        'The output file `%s` already exists. Use the '
                        '`-f` or `-a` option to overwrite or append to it.'
                        % output
                    )
                    sys.exit(1)

            fh = output_path.open('a' if append else 'w') if write else sys.stdout
            print(f'Writing to {fh}', file=sys.stderr)
        else:
            fh = sys.stdout

        print(AdminApp(app, model_res, **options), file=fh)

        if output:
            fh.close()
