"""Helpers for discovering installed apps and their models."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from django.apps import AppConfig
from django.apps.registry import apps
from django.conf import settings
from django.db import models


def get_models(app: AppConfig) -> Iterator[type[models.Model]]:
    """Yield every model registered on ``app``."""
    yield from app.get_models()


def get_apps() -> Iterator[tuple[str, AppConfig]]:
    """Yield ``(name, app_config)`` for every installed app.

    Each app is yielded twice: once under its full dotted path and once
    under its short (last component) name so both can be used as lookups.
    """
    for app_config in apps.get_app_configs():
        yield app_config.name, app_config
        yield app_config.name.rsplit('.')[-1], app_config


def get_local_apps() -> list[AppConfig]:
    """Return the apps that live inside the project (not site-packages)."""
    local_app_configs: list[AppConfig] = []
    # Absolute path of the project's base directory.
    project_root: Path = Path(settings.BASE_DIR).resolve()

    # If the virtual environment lives inside the project directory, skip it.
    venv_path: Path = project_root / 'venv'

    for app_config in apps.get_app_configs():
        app_path: Path = Path(app_config.path).resolve()
        # Keep apps within the project but outside the virtualenv and
        # site-packages.
        if (
            (project_root in app_path.parents or app_path == project_root)
            and venv_path not in app_path.parents
            and 'site-packages' not in str(app_path)
        ):
            local_app_configs.append(app_config)
    return local_app_configs
