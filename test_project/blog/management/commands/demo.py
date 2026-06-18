"""One-command launcher for the live Django Admin Generator demo.

    python manage.py demo            # migrate + seed + serve, open browser
    python manage.py demo --regenerate   # also re-run the generator first

Prints the URL and credentials first (the reliable path) and then tries to
open a browser before handing off to ``runserver``.
"""

import threading
import webbrowser

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandParser

DEFAULT_ADDR = '127.0.0.1:8000'


class Command(BaseCommand):
    help = 'Set up and launch the live Django Admin Generator demo.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--addr',
            default=DEFAULT_ADDR,
            help=f'Address:port for the dev server (default {DEFAULT_ADDR}).',
        )
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Re-run admin_generator to rewrite blog/admin.py first.',
        )
        parser.add_argument(
            '--no-browser',
            action='store_true',
            help='Do not try to open a web browser.',
        )

    def handle(self, *args, **options):
        addr = options['addr']
        self.stdout.write('Setting up the demo database...')
        call_command('migrate', verbosity=0)
        call_command('seed_demo')

        if options['regenerate']:
            self.stdout.write('Regenerating blog/admin.py...')
            call_command(
                'admin_generator',
                'blog',
                prepopulated_field_names=['slug=name', 'slug=title'],
                write=True,
                force=True,
            )

        url = f'http://{addr}/admin/'
        self.stdout.write(self.style.SUCCESS('\nDemo ready!'))
        self.stdout.write(f'  Open:  {url}')
        self.stdout.write('  Login: admin / admin\n')
        self.stdout.write('Press CTRL-C to stop the server.\n')

        if not options['no_browser']:
            threading.Timer(1.5, lambda: webbrowser.open(url)).start()

        call_command('runserver', addr, use_reloader=False)
