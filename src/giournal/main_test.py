import unittest
from tempfile import (
    TemporaryDirectory,
    mkstemp,
)
from typing import List
from unittest.mock import patch, MagicMock

from .journal_configuration import JournalConfiguration, initialise_journal_config


class MainTest(unittest.TestCase):
    @patch("builtins.input")
    def test_initialise_journal_config(self, input_mock: MagicMock) -> None:
        with TemporaryDirectory() as journal_directory:
            configuration_file_path: str
            _, configuration_file_path = mkstemp()
            inputs: List[str] = [journal_directory, "false", "no"]
            input_mock.side_effect = lambda _: inputs.pop(0)
            journal_config: JournalConfiguration = initialise_journal_config(
                configuration_file_path
            )
        self.assertEqual(journal_config.journal_path, journal_directory)
        self.assertFalse(journal_config.sync_to_git)
        self.assertFalse(journal_config.use_keychain)
