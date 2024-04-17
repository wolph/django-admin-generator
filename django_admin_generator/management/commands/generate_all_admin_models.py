import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    """
    Generate admin.py for each installed app in the apps directory
    Usage: python manage.py generate_admin_models <name the dir where your apps are located>
    """
    help = 'Generate admin.py for each installed app in the apps directory'

    def add_arguments(self, parser):
        parser.add_argument('apps_dir', type=str, help='Directory where the apps are located')

    def handle(self, *args, **options):
        apps_dir = options['apps_dir']

        for app_config in apps.get_app_configs():
            if apps_dir in Path(app_config.path).parents:
                app_name = app_config.name
                print(f"Generating admin.py for {app_name}")

                # Command to generate admin file
                command = f"python manage.py admin_generator {app_name} > {app_config.path}/admin.py"
                os.system(command)

                self.stdout.write(self.style.SUCCESS(f'Successfully created admin.py for {app_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping {app_config.name}, not in apps directory'))
