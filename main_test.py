from tempfile import (
    mktemp,
    TemporaryFile,
    TemporaryDirectory,
    NamedTemporaryFile,
    mkstemp,
)
from typing import List, Tuple
from unittest.mock import patch, MagicMock

from journal_configuration import JournalConfiguration
from main import initialise_journal_config


@patch("builtins.input")
def test_initialise_journal_config(input_mock: MagicMock) -> None:
    with TemporaryDirectory() as journal_directory:
        configuration_file_path: str
        _, configuration_file_path = mkstemp()
        inputs: List[str] = [journal_directory, "false", "no"]
        input_mock.side_effect = lambda _: inputs.pop(0)
        journal_config: JournalConfiguration = initialise_journal_config(
            configuration_file_path
        )

    assert journal_config.journal_path == journal_directory
    assert journal_config.sync_to_git is False
    assert journal_config.use_keychain is False
