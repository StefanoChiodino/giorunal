""" Based on https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password """
import argparse
import os
import sys
from pathlib import Path
from typing import Callable, Optional, List

from helpers.keychain import (
    get_password_from_keychain_with_fallback,
    get_password_from_keychain,
)
from journal_configuration import JournalConfiguration
from journal import Journal

CONFIG_PATH = f"{str(Path.home())}/.giournal"


def initialise_journal(journal_path: str) -> None:
    print(f"Journal will be created at '{journal_path}'.")
    password: str

    safe_make_dir_and_file(journal_path)


def get_journal(config_path: str) -> Journal:
    journal_configuration: JournalConfiguration = get_journal_configuration(config_path)

    password = get_password_from_keychain()
    if not os.path.exists(journal_configuration.journal_path):
        initialise_journal(journal_configuration.journal_path)

    return Journal(str(journal_configuration.journal_path), password)


def safe_make_dir_and_file(file_path: str) -> None:
    journal_path: Path = Path(file_path)
    if not os.path.exists(journal_path.parent):
        os.mkdir(journal_path.parent)
    if not os.path.exists(journal_path):
        open(journal_path, "a").close()


def get_journal_configuration(path: str) -> JournalConfiguration:
    if not os.path.exists(path):
        initialise_journal_config(path)
    journal_configuration: JournalConfiguration = JournalConfiguration().load(path)
    return journal_configuration


def initialise_journal_config(config_path) -> JournalConfiguration:
    print(f"Creating journal config at '{config_path}'")
    default_journal_path: str = f"{str(Path.home())}/journal"
    journal_path = (
        input(f"Journal path [{default_journal_path}]: ") or default_journal_path
    )
    default_use_keychain: bool = True
    use_keychain = (
        input(
            f"Do you want to store your password to your keychain? [{default_use_keychain}]: "
        )
        or default_use_keychain
    )
    default_sync_to_git: bool = True
    sync_to_git = (
        input(f"Do you want to sync your journal to git? [{default_sync_to_git}]: ")
        or default_sync_to_git
    )
    safe_make_dir_and_file(config_path)
    journal_config: JournalConfiguration = JournalConfiguration(
        file_path=journal_path,
        use_keychain=_parse_true_false(use_keychain, default_use_keychain),
        sync_to_git=_parse_true_false(sync_to_git, default_sync_to_git),
    )
    journal_config.store(config_path)
    return journal_config


def _parse_true_false(input: str, default: bool) -> bool:
    if input.lower() in ["true", "yes"]:
        return True
    if input.lower() in ["false", "no"]:
        return False
    return default


def print_entries() -> None:
    journal: Journal = get_journal(CONFIG_PATH)
    entries: str = journal.list_entries()
    print(entries)


def main() -> None:
    journal_configuration: JournalConfiguration = JournalConfiguration()
    journal_configuration.load(CONFIG_PATH)

    args = _parse_args(sys.argv[1:])

    if isinstance(args.callable, Callable):
        args.callable()
    elif args.text:
        journal: Journal = get_journal(CONFIG_PATH)
        journal.add_entry(" ".join(args.text).strip())


def _parse_args(args: List[str]) -> argparse.Namespace:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--list",
        action="store_const",
        const=print_entries,
        dest="callable",
        help="lists all the entries",
    )
    argument_parser.add_argument("text", metavar="", nargs="*")
    args: argparse.Namespace = argument_parser.parse_args(args)
    return args


if __name__ == "__main__":
    main()
