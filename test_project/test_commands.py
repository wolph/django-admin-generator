import pytest
from django_admin_generator.management.commands import admin_generator

# Low thresholds force foreign keys / m2m into raw_id_fields and every field
# into list_filter, exercising those branches against the empty test DB.
DEFAULTS = {
    'date_hierarchy_names': ('created_at', 'zzz_missing'),
    'date_hierarchy_threshold': 0,
    'list_filter_threshold': 0,
    'raw_id_threshold': 0,
    'prepopulated_field_names': (
        'slug=name',  # complete on Category/Author/Tag, incomplete on Post
        'missing=name',  # key absent from every model -> skipped
        # Long, complete on Post -> exercises the multi-line dict rendering.
        'slug=title,body,created_at,published_at',
    ),
}

# High thresholds flip the same decisions the other way (list_filter instead of
# raw_id, date_hierarchy gets assigned).
DEFAULTS_FILTERED = DEFAULTS.copy()
DEFAULTS_FILTERED['date_hierarchy_threshold'] = 250
DEFAULTS_FILTERED['list_filter_threshold'] = 250
DEFAULTS_FILTERED['raw_id_threshold'] = 250

BLOG = 'test_project.blog'


@pytest.fixture
def command(monkeypatch):
    return admin_generator.Command()


def check_output(capsys):
    out, _err = capsys.readouterr()
    # Strip comments so `compile` doesn't choke on encoding lines.
    out = '\n'.join(
        line for line in out.split('\n') if not line.startswith('#')
    )
    compile(out, 'admin.py', 'exec')


def test_no_app(command):
    with pytest.raises(SystemExit):
        command.handle('some-non-existing-app')


def test_parser(command):
    command.create_parser('manage.py', 'admin_generator')


def test_parser_append_options(command):
    # The append options use the generator's option names as their dest and
    # append to (a copy of) the list defaults without crashing.
    parser = command.create_parser('manage.py', 'admin_generator')
    ns = parser.parse_args(
        ['myapp', '-s', 'title', '-d', 'published_at', '-p', 'slug=title'],
    )
    assert ns.search_field_names == ['name', 'slug', 'title']
    assert ns.date_hierarchy_names == [
        'joined_at',
        'updated_at',
        'created_at',
        'published_at',
    ]
    assert ns.prepopulated_field_names == ['slug=name', 'slug=title']


@pytest.mark.django_db
def test_blog(command, capsys):
    command.handle(app=BLOG, **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_blog_filtered(command, capsys):
    command.handle(app=BLOG, **DEFAULTS_FILTERED)
    check_output(capsys)


@pytest.mark.django_db
def test_blog_post_only(command, capsys):
    command.handle(app=BLOG, models=['post'], **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_auth(command, capsys):
    command.handle(app='django.contrib.auth', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_auth_filtered(command, capsys):
    command.handle(app='django.contrib.auth', **DEFAULTS_FILTERED)
    check_output(capsys)


def test_no_database(command, capsys):
    command.handle(app=BLOG, no_query_db=True, **DEFAULTS_FILTERED)
    check_output(capsys)


@pytest.mark.django_db
def test_all(command, capsys):
    command.handle(app='all', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_output_to_stdout(command, capsys):
    # `output` without a path separator resolves against the app dir, but with
    # `write` off the result still goes to stdout. Use a name that does not
    # exist in the app dir so the overwrite guard is not triggered.
    command.handle(app=BLOG, output='generated_admin.py', **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_write_to_file(command, tmp_path):
    output = tmp_path / 'admin.py'
    command.handle(app=BLOG, output=str(output), write=True, **DEFAULTS)
    assert 'ModelAdminBase' in output.read_text()


@pytest.mark.django_db
def test_write_existing_without_force(command, tmp_path):
    output = tmp_path / 'admin.py'
    output.write_text('# existing\n')
    with pytest.raises(SystemExit):
        command.handle(app=BLOG, output=str(output), write=True, **DEFAULTS)


@pytest.mark.django_db
def test_write_existing_with_force(command, tmp_path):
    output = tmp_path / 'admin.py'
    output.write_text('# existing\n')
    command.handle(
        app=BLOG, output=str(output), write=True, force=True, **DEFAULTS
    )
    assert 'ModelAdminBase' in output.read_text()


@pytest.mark.django_db
def test_write_existing_with_append(command, tmp_path):
    output = tmp_path / 'admin.py'
    output.write_text('# existing\n')
    command.handle(
        app=BLOG, output=str(output), write=True, append=True, **DEFAULTS
    )
    contents = output.read_text()
    assert contents.startswith('# existing')
    assert 'ModelAdminBase' in contents


@pytest.mark.django_db
def test_disable_json_widget(command, capsys):
    command.handle(app=BLOG, disable_json_widget=True, **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_disable_auto_complete(command, capsys):
    # auto_complete falsy -> autocomplete pass skipped; m2m goes through the
    # raw-id path with raw_id_threshold 0 (count < 0 is False, nothing added).
    command.handle(app=BLOG, disable_auto_complete=True, **DEFAULTS)
    check_output(capsys)


@pytest.mark.django_db
def test_disable_auto_complete_raw_id(command, capsys):
    # Same path but with a high threshold, so the m2m field IS added to
    # raw_id_fields (the yield branch).
    command.handle(app=BLOG, disable_auto_complete=True, **DEFAULTS_FILTERED)
    check_output(capsys)


@pytest.mark.django_db
def test_specific_auto_complete(command, capsys):
    # tags is explicitly auto-completed -> skipped by the raw-id m2m pass.
    command.handle(app=BLOG, auto_complete=['tags'], **DEFAULTS_FILTERED)
    check_output(capsys)


@pytest.mark.django_db
def test_other_auto_complete(command, capsys):
    # An auto_complete list that does NOT include tags -> the membership test
    # is exercised for both outcomes.
    command.handle(
        app=BLOG, auto_complete=['nonexistent'], **DEFAULTS_FILTERED
    )
    check_output(capsys)
