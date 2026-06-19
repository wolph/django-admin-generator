"""``admin_generator`` management command entry point."""

from __future__ import annotations

import pathlib
import re
import sys
import typing
from collections.abc import Mapping

from django.apps import AppConfig
from django.core.management.base import CommandParser
from django_utils.management.commands import base_command
from python_utils import logger

from django_admin_generator.constants import (
    DATE_HIERARCHY_NAMES,
    DATE_HIERARCHY_THRESHOLD,
    LIST_FILTER_THRESHOLD,
    PREPOPULATED_FIELD_NAMES,
    RAW_ID_THRESHOLD,
    SEARCH_FIELD_NAMES,
)
from django_admin_generator.discovery import get_apps, get_local_apps
from django_admin_generator.generators import AdminApp


class Command(base_command.CustomBaseCommand):  # type: ignore[misc]
    help = """Generate a `admin.py` file for the given app (models)"""
    can_import_settings = True
    requires_system_checks = ('__all__',)

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)

        parser.add_argument(
            '-s',
            '--search-field',
            dest='search_field_names',
            action='append',
            default=list(SEARCH_FIELD_NAMES),
            help='Fields named like this will be added to `search_fields`',
        )
        parser.add_argument(
            '-d',
            '--date-hierarchy',
            dest='date_hierarchy_names',
            action='append',
            default=list(DATE_HIERARCHY_NAMES),
            help='A field named like this will be set as `date_hierarchy`',
        )
        parser.add_argument(
            '--date-hierarchy-threshold',
            type=int,
            default=DATE_HIERARCHY_THRESHOLD,
            metavar='DATE_HIERARCHY_THRESHOLD',
            help='If a model has less than DATE_HIERARCHY_THRESHOLD items '
            'it will be added to `date_hierarchy`',
        )
        parser.add_argument(
            '-p',
            '--prepopulated-fields',
            dest='prepopulated_field_names',
            action='append',
            default=list(PREPOPULATED_FIELD_NAMES),
            help='These fields will be prepopulated by the other field.'
            'The field names can be specified like `spam=eggA,eggB,eggC`',
        )
        parser.add_argument(
            '-l',
            '--list-filter-threshold',
            type=int,
            default=LIST_FILTER_THRESHOLD,
            metavar='LIST_FILTER_THRESHOLD',
            help='If a foreign key/field has less than LIST_FILTER_THRESHOLD '
            'items it will be added to `list_filter`',
        )
        parser.add_argument(
            '-r',
            '--raw-id-threshold',
            type=int,
            default=RAW_ID_THRESHOLD,
            metavar='RAW_ID_THRESHOLD',
            help='If a foreign key has more than RAW_ID_THRESHOLD items '
            'it will be added to `list_filter`',
        )
        parser.add_argument(
            '-n',
            '--no-query-db',
            action='store_true',
            dest='no_query_db',
            help="Don't query the database in order to decide whether "
            'fields/relationships are added to `list_filter`',
        )
        parser.add_argument(
            '-w',
            '--write',
            action='store_true',
            help='Write the output to the admin.py file(s)',
        )
        parser.add_argument(
            '-o',
            '--output',
            default='admin.py',
            help='Output file name',
        )
        parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            help='Overwrite the output file if it exists',
        )
        parser.add_argument(
            '-a',
            '--append',
            action='store_true',
            help='Append the output to the output file if it exists',
        )
        parser.add_argument(
            'app',
            help='App to generate admin definitions for, use `all` to '
            'generate for all local (i.e. not in site-packages) apps',
        )
        parser.add_argument(
            'models',
            nargs='*',
            help='Regular expressions to filter the models by',
        )
        parser.add_argument(
            '--disable-json-widget',
            action='store_true',
            help='Disable the JSON widget import and formfield override',
        )
        parser.add_argument(
            '--enable-reversion',
            action='store_true',
            help='Enable django-reversion support',
        )
        parser.add_argument(
            '--reversion-admin-regex',
            default=r'.*',
            help='Regular expression to filter the models by for reversion',
        )
        parser.add_argument(
            '--reversion-admin-class',
            default='VersionAdmin',
            help='The base class for the ModelAdmin classes for reversion',
        )
        parser.add_argument(
            '--reversion-admin-class-import',
            default='from reversion.admin import VersionAdmin',
            help='The import statement for the base class for the ModelAdmin '
            'classes for reversion',
        )
        parser.add_argument(
            '--admin-class',
            default='admin.ModelAdmin',
            help='The base class for the ModelAdmin classes',
        )
        parser.add_argument(
            '--admin-class-import',
            default='',
            help='The import statement for the base class for the ModelAdmin '
            'classes if it is not the Django default',
        )
        parser.add_argument(
            '--disable-auto-complete',
            action='store_true',
            help='Disable the auto-complete feature for the many-to-many '
            'fields',
        )
        parser.add_argument(
            '--auto-complete',
            action='append',
            help='Enable the auto-complete feature only for the specified '
            'many-to-many fields',
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: logger._ExcInfoType = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        # This replaces the regular warning method from the CustomBaseCommand
        # since some Django installations capture all logging output
        # unfortunately.
        sys.stderr.write(str(msg))
        sys.stderr.write('\n')

    def handle(
        self,
        app: str | None = None,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        super().handle(*args, **kwargs)

        if app == 'all':
            for app_config in get_local_apps():
                self.handle_app(app_config, [], **kwargs)
        else:
            installed_apps: dict[str, AppConfig] = dict(get_apps())

            target = installed_apps.get(app) if app else None
            if target is None:
                self.warning(
                    'This command requires an existing app name as argument'
                )
                self.warning('Available apps:')
                for name in sorted(installed_apps):
                    self.warning(f'    {name}')
                sys.exit(1)

            model_res: list[re.Pattern[str]] = [
                re.compile(model, re.IGNORECASE)
                for model in kwargs.get('models', [])
            ]

            self.handle_app(target, model_res, **kwargs)

    def handle_app(
        self,
        app: AppConfig,
        model_res: list[re.Pattern[str]],
        write: bool = False,
        output: str | None = None,
        force: bool = False,
        append: bool = False,
        **options: typing.Any,
    ) -> None:
        fh: typing.IO[str]
        if output:
            if '/' in output or '\\' in output:
                output_path = pathlib.Path(output)
            else:
                output_path = pathlib.Path(app.path) / output

            print(f'Writing {app.name} to {output_path}', file=sys.stderr)

            if output_path.exists() and not force and not append:
                self.warning(
                    f'The output file `{output}` already exists. Use the '
                    '`-f` or `-a` option to overwrite or append to it.'
                )
                sys.exit(1)

            fh = (
                output_path.open('a' if append else 'w')
                if write
                else sys.stdout
            )
            print(f'Writing to {fh}', file=sys.stderr)
        else:
            fh = sys.stdout

        print(AdminApp(app, model_res, **options), file=fh)

        if output and fh is not sys.stdout:
            fh.close()
