from tempfile import TemporaryDirectory, mkstemp
from unittest.mock import patch

from journal_configuration import JournalConfiguration


def test_can_create_journal_config() -> None:
    journal_configuration: JournalConfiguration = JournalConfiguration("/")
    assert journal_configuration is not None


def test_can_store_and_load_from_file() -> None:
    journal_configuration: JournalConfiguration = JournalConfiguration("/")
    stored_value: str
    configuration_file_path: str
    _, configuration_file_path = mkstemp()
    journal_configuration.store(configuration_file_path)
    loaded_journal_configuration: JournalConfiguration = JournalConfiguration()
    loaded_journal_configuration.load(configuration_file_path)
    assert loaded_journal_configuration.journal_path == "/"
