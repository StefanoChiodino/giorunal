import unittest
from tempfile import TemporaryDirectory, mkstemp
from unittest.mock import patch

from .journal_configuration import JournalConfiguration


class TestJournalConfiguration(unittest.TestCase):
    def test_can_create_journal_config(self) -> None:
        journal_configuration: JournalConfiguration = JournalConfiguration("/")
        self.assertIsNotNone(journal_configuration)

    def test_can_store_and_load_from_file(self) -> None:
        journal_configuration: JournalConfiguration = JournalConfiguration("/")
        stored_value: str
        configuration_file_path: str
        _, configuration_file_path = mkstemp()
        journal_configuration.store(configuration_file_path)
        loaded_journal_configuration: JournalConfiguration = JournalConfiguration()
        loaded_journal_configuration.load(configuration_file_path)
        self.assertEqual(loaded_journal_configuration.journal_path, "/")
