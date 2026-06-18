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
        'this_should_be_something_really_long_b',
    ),
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
    out, _err = capsys.readouterr()
    # Strip out encodings (and all other comments) so `compile` doesn't break
    out = '\n'.join(
        line for line in out.split('\n') if not line.startswith('#')
    )
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
    command.handle(
        app='django.contrib.auth', models=['user'], **DEFAULTS_FILTERED
    )
    check_output(capsys)


def test_no_database(command, capsys):
    command.handle(
        app='django.contrib.auth',
        models=['user'],
        no_query_db=True,
        **DEFAULTS_FILTERED,
    )
    check_output(capsys)


@pytest.mark.django_db
def test_all(command, capsys):
    command.handle(app='all', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_output_to_stdout(command, capsys):
    # `output` without a path separator is resolved against the app dir, but
    # with `write` disabled the result is still printed to stdout.
    command.handle(app='test_project.test_app', output='admin.py', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_write_to_file(command, tmp_path):
    output = tmp_path / 'admin.py'
    command.handle(
        app='test_project.test_app',
        output=str(output),
        write=True,
        **DEFAULTS,
    )
    assert 'ModelAdminBase' in output.read_text()


@pytest.mark.django_db
def test_write_existing_without_force(command, tmp_path):
    output = tmp_path / 'admin.py'
    output.write_text('# existing\n')
    with pytest.raises(SystemExit):
        command.handle(
            app='test_project.test_app',
            output=str(output),
            write=True,
            **DEFAULTS,
        )


@pytest.mark.django_db
def test_write_existing_with_force(command, tmp_path):
    output = tmp_path / 'admin.py'
    output.write_text('# existing\n')
    command.handle(
        app='test_project.test_app',
        output=str(output),
        write=True,
        force=True,
        **DEFAULTS,
    )
    assert 'ModelAdminBase' in output.read_text()


@pytest.mark.django_db
def test_write_existing_with_append(command, tmp_path):
    output = tmp_path / 'admin.py'
    output.write_text('# existing\n')
    command.handle(
        app='test_project.test_app',
        output=str(output),
        write=True,
        append=True,
        **DEFAULTS,
    )
    contents = output.read_text()
    assert contents.startswith('# existing')
    assert 'ModelAdminBase' in contents


@pytest.mark.django_db
def test_disable_json_widget(command, capsys):
    command.handle(
        app='test_project.test_app', disable_json_widget=True, **DEFAULTS
    )
    check_output(capsys)


@pytest.mark.django_db
def test_disable_auto_complete(command, capsys):
    # `auto_complete` becomes falsy so the autocomplete pass is skipped; with
    # `raw_id_threshold` of 0 the m2m fields stay out of `raw_id_fields`.
    command.handle(
        app='django.contrib.auth',
        disable_auto_complete=True,
        **DEFAULTS,
    )
    check_output(capsys)


@pytest.mark.django_db
def test_specific_auto_complete(command, capsys):
    # `auto_complete` is an explicit list: listed m2m fields are auto-completed
    # while the others fall through to the raw-id/list-filter handling.
    command.handle(
        app='django.contrib.auth',
        auto_complete=['groups'],
        **DEFAULTS_FILTERED,
    )
    check_output(capsys)
