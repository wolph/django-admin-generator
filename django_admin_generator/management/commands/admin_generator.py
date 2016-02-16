import re
import sys
import six
import optparse
from django_utils.management.commands import base_command
from django.db import models

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

LIST_FILTER_THRESHOLD = 25
RAW_ID_THRESHOLD = 100
NO_QUERY_DB = False

PRINT_IMPORTS = '''# vim: set fileencoding=utf-8 :
from django.contrib import admin

from . import models
'''

PRINT_ADMIN_CLASS = '''

class %(name)sAdmin(admin.ModelAdmin):
%(class_)s
'''

PRINT_ADMIN_REGISTRATION_METHOD = '''

def _register(model, admin_class):
    admin.site.register(model, admin_class)

'''

PRINT_ADMIN_REGISTRATION = '''
_register(models.%(name)s, %(name)sAdmin)'''

PRINT_ADMIN_REGISTRATION_LONG = '''
_register(
    models.%(name)s,
    %(name)sAdmin)'''

PRINT_ADMIN_PROPERTY = '''
    %(key)s = %(value)s'''

#Account for removed functions in newer versions of django
try:
    from django.apps import apps
    get_model = apps.get_model
except:
    from django.db.models.loading import get_model

try:
    from django.conf import settings
    class NameClass:
        def __init__(self, name):
            self.__name__=name
    def get_apps():
        return (NameClass(app_name) for app_name in settings.INSTALLED_APPS)
    get_apps() #Make sure no error is thrown
except:
    get_apps=models.get_apps

try:
    get_models=apps.get_models
except:
    get_models=models.get_models
#End of version upgrade code

class AdminApp(object):
    def __init__(self, app, model_res, **options):
        self.app = app
        self.model_res = model_res
        self.options = options

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

    def _unicode_generator(self):
        yield PRINT_IMPORTS

        admin_model_names = []
        for admin_model in self:
            yield PRINT_ADMIN_CLASS % dict(
                name=admin_model.name,
                class_=admin_model,
            )
            admin_model_names.append(admin_model.name)

        yield PRINT_ADMIN_REGISTRATION_METHOD

        for name in admin_model_names:
            row = PRINT_ADMIN_REGISTRATION % dict(name=name)
            if len(row) > MAX_LINE_WIDTH:
                row = PRINT_ADMIN_REGISTRATION_LONG % dict(name=name)
            yield row

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
        'search_fields',
        'prepopulated_fields',
        'date_hierarchy',
    )

    def __init__(self, model, raw_id_threshold=RAW_ID_THRESHOLD,
                 list_filter_threshold=LIST_FILTER_THRESHOLD,
                 search_field_names=SEARCH_FIELD_NAMES,
                 date_hierarchy_names=DATE_HIERARCHY_NAMES,
                 prepopulated_field_names=PREPOPULATED_FIELD_NAMES,
                 no_query_db=NO_QUERY_DB, **options):
        self.model = model
        self.list_display = []
        self.list_filter = []
        self.raw_id_fields = []
        self.search_fields = []
        self.prepopulated_fields = {}
        self.date_hierarchy = None
        self.search_field_names = search_field_names
        self.raw_id_threshold = raw_id_threshold
        self.list_filter_threshold = list_filter_threshold
        self.date_hierarchy_names = date_hierarchy_names
        self.prepopulated_field_names = prepopulated_field_names
        self.query_db = not no_query_db

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
            related_model = getattr(field.related, 'related_model',
                                    field.related.model)
            related_objects = related_model.objects.all()
            if(related_objects[:raw_id_threshold].count() < raw_id_threshold):
                yield field.name

    def _process_fields(self, meta):
        parent_fields = meta.parents.values()
        for field in meta.fields:
            name = self._process_field(field, parent_fields)
            if name:  # pragma: no cover
                yield name

    def _process_foreign_key(self, field):
        raw_id_threshold = self.raw_id_threshold
        list_filter_threshold = self.list_filter_threshold
        max_count = max(list_filter_threshold, raw_id_threshold)
        related_model = getattr(field.related, 'related_model',
                                field.related.model)
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

        if self.query_db:
            self.raw_id_fields += list(self._process_many_to_many(meta))
        field_names = list(self._process_fields(meta))

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
    option_list = base_command.CustomBaseCommand.option_list + (
        optparse.make_option(
            '-s', '--search-field', action='append',
            default=SEARCH_FIELD_NAMES,
            help='Fields named like this will be added to `search_fields`'
            ' [default: %default]'),
        optparse.make_option(
            '-d', '--date-hierarchy', action='append',
            default=DATE_HIERARCHY_NAMES,
            help='A field named like this will be set as `date_hierarchy`'
            ' [default: %default]'),
        optparse.make_option(
            '-p', '--prepopulated-fields', action='append',
            default=PREPOPULATED_FIELD_NAMES,
            help='These fields will be prepopulated by the other field.'
            'The field names can be specified like `spam=eggA,eggB,eggC`'
            ' [default: %default]'),
        optparse.make_option(
            '-l', '--list-filter-threshold', type='int',
            default=LIST_FILTER_THRESHOLD, metavar='LIST_FILTER_THRESHOLD',
            help='If a foreign key has less than LIST_FILTER_THRESHOLD items '
            'it will be added to `list_filter` [default: %default]'),
        optparse.make_option(
            '-r', '--raw-id-threshold', type='int',
            default=RAW_ID_THRESHOLD, metavar='RAW_ID_THRESHOLD',
            help='If a foreign key has more than RAW_ID_THRESHOLD items '
            'it will be added to `list_filter` [default: %default]'),
        optparse.make_option(
            '-n', '--no-query-db', action="store_true", dest='no_query_db',
            help='Don\'t query the database in order to decide whether '
            'relationships are added to `list_filter`'),
    )
    can_import_settings = True
    requires_system_checks = True

    def warning(self, message):
        # This replaces the regular warning method from the CustomBaseCommand
        # since some Django installations capture all logging output
        # unfortunately
        sys.stderr.write(message)
        sys.stderr.write('\n')

    def handle(self, *args, **kwargs):
        super(Command, self).handle(*args, **kwargs)

        installed_apps = dict(
            (a.__name__.rsplit('.', 1)[0], a)
            for a in get_apps())

        # Make sure we always have args
        if not args:
            args = [False]

        app = installed_apps.get(args[0])
        if not app:
            self.warning('This command requires an existing app name as '
                         'argument')
            self.warning('Available apps:')
            for app in sorted(installed_apps):
                self.warning('    %s' % app)
            sys.exit(1)

        model_res = []
        for arg in args[1:]:
            model_res.append(re.compile(arg, re.IGNORECASE))

        self.handle_app(app, model_res, **kwargs)

    def handle_app(self, app, model_res, **options):
        print(AdminApp(app, model_res, **options))


