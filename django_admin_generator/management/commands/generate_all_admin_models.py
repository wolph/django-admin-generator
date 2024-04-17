from django.core.management.base import BaseCommand
from django.apps import apps
import os
from pathlib import Path

class Command(BaseCommand):
    """
    Generate admin.py for each installed app in the specified apps directory.
    Usage: python manage.py generate_admin_models <path to apps directory>
    """
    help = 'Generate admin.py for each installed app in the specified apps directory'

    def add_arguments(self, parser):
        parser.add_argument('apps_dir', type=str, help='Directory where the apps are located')

    def handle(self, *args, **options):
        apps_dir = Path(options['apps_dir']).resolve()

        # Validate the apps directory
        if not apps_dir.exists() or not apps_dir.is_dir():
            self.stdout.write(self.style.ERROR(f"The specified apps directory does not exist: {apps_dir}"))
            return

        for app_config in apps.get_app_configs():
            app_path = Path(app_config.path).resolve()

            if apps_dir in app_path.parents:
                app_name = app_config.name
                print(f"Generating admin.py for {app_name}")

                # Command to generate admin file
                command = f"python manage.py admin_generator {app_name} > {app_path}/admin.py"
                os.system(command)

                self.stdout.write(self.style.SUCCESS(f'Successfully created admin.py for {app_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipping {app_config.name}, not in specified apps directory'))

