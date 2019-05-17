import six
import pytest

from django_admin_generator.management.commands import admin_generator

DEFAULTS = {
    'date_hierarchy_names': 'date_joined',
    'date_hierarchy_threshold': 0,
    'list_filter_threshold': 0,
    'raw_id_threshold': 0,
    'prepopulated_field_names': (
        'username=first_name',
        'last_name=full_name',
        'this_should_be_something_really_long_a='
        'this_should_be_something_really_long_b'),
}

DEFAULTS_FILTERED = DEFAULTS.copy()
DEFAULTS_FILTERED['date_hierarchy_threshold'] = 250
DEFAULTS_FILTERED['list_filter_threshold'] = 250
DEFAULTS_FILTERED['raw_id_threshold'] = 250


@pytest.fixture
def command(monkeypatch):
    return admin_generator.Command()


def test_no_app(command):
    with pytest.raises(SystemExit):
        command.handle('some-non-existing-app')


def test_parser(command):
    command.create_parser('manage.py', 'admin_generator')


def check_output(capsys):
    out, err = capsys.readouterr()
    # Strip out encodings (and all other comments) so `compile` doesn't break
    out = six.u('\n').join(line for line in out.split('\n')
                           if not line.startswith('#'))
    compile(out, 'admin.py', 'exec')


@pytest.mark.django_db
def test_app(command, capsys, monkeypatch):
    command = admin_generator.Command()
    command.handle(app='test_project.test_app', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_auth(command, capsys):
    command.handle(app='django.contrib.auth', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_auth_user(command, capsys):
    command.handle(app='django.contrib.auth', models=['user'], **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_app_filter(command, capsys):
    command.handle(app='test_project.test_app', **DEFAULTS_FILTERED)
    check_output(capsys)


@pytest.mark.django_db
def test_auth_filter(command, capsys):
    command.handle(app='django.contrib.auth', **DEFAULTS_FILTERED)
    check_output(capsys)


@pytest.mark.django_db
def test_auth_user_filter(command, capsys):
    command.handle(app='django.contrib.auth', models=['user'],
                   **DEFAULTS_FILTERED)
    check_output(capsys)


def test_no_database(command, capsys):
    command.handle(app='django.contrib.auth', models=['user'],
                   no_query_db=True, **DEFAULTS_FILTERED)
    check_output(capsys)

