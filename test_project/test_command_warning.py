import pytest
from django_admin_generator.management.commands.admin_generator import Command


@pytest.mark.parametrize('from_class', [False, True])
def test_warning_writes_to_stderr(
    capsys: pytest.CaptureFixture[str], from_class: bool
) -> None:
    command: type[Command] | Command = Command if from_class else Command()
    command.warning('Missing app')
    captured: pytest.CaptureResult[str] = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'Missing app\n'
