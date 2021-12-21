#!/usr/bin/env python3

import argparse
import datetime
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, List
from json.decoder import JSONDecodeError
from typing.io import IO

from journal_configuration import JournalConfiguration, initialise_journal_config
from journal import Journal, get_journal, FILENAME_DATETIME_FORMAT

CONFIG_PATH = f"{str(Path.home())}/.giournal"


def print_entries() -> None:
    journal: Journal = get_journal(CONFIG_PATH)
    entries: str = journal.list_entries()
    print(entries)


def decrypt() -> None:
    journal: Journal = get_journal(CONFIG_PATH)
    journal.decrypt()
    print("All entries have been decrypted, press any key to encrypt them again.")
    input()
    journal.encrypt()


def encrypt() -> None:
    journal: Journal = get_journal(CONFIG_PATH)
    journal.encrypt()


def editor() -> None:
    journal_configuration: JournalConfiguration = get_or_create_config()
    journal: Journal = Journal(journal_configuration)
    directory: str
    with tempfile.TemporaryDirectory() as directory:
        file_name: str = f"{datetime.datetime.now().strftime(FILENAME_DATETIME_FORMAT)}.md"
        file_path: str = os.path.join(directory, file_name)
        subprocess.call(("code", "--wait", file_path))
        with open(file_path, "r") as file:
            journal.add_entry("".join(file.readlines()))


def _parse_args(args: List[str]) -> argparse.Namespace:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--list",
        action="store_const",
        const=print_entries,
        dest="callable",
        help="Lists all the entries.",
    )
    argument_parser.add_argument(
        "--decrypt",
        action="store_const",
        const=decrypt,
        dest="callable",
        help="Decrypt entries, waits for input, re-encrypts all entries.",
    )
    argument_parser.add_argument(
        "--encrypt",
        action="store_const",
        const=encrypt,
        dest="callable",
        help="encrypts all entries.",
    )
    argument_parser.add_argument(
        "--editor",
        action="store_const",
        const=editor,
        dest="callable",
        help="Starts a new note in your editor.",
    )
    argument_parser.add_argument("text", metavar="", nargs="*")
    args: argparse.Namespace = argument_parser.parse_args(args)
    return args


def get_or_create_config() -> JournalConfiguration:
    try:
        journal_configuration: JournalConfiguration = JournalConfiguration.load(CONFIG_PATH)
    except (JSONDecodeError, FileNotFoundError) as _:
        initialise_journal_config(CONFIG_PATH)
        journal_configuration: JournalConfiguration = JournalConfiguration.load(CONFIG_PATH)
    return journal_configuration


def main() -> None:
    journal_configuration = get_or_create_config()

    args = _parse_args(sys.argv[1:])

    if isinstance(args.callable, Callable):
        args.callable()
    elif args.text:
        journal: Journal = Journal(journal_configuration)
        journal.add_entry(" ".join(args.text).strip())


if __name__ == "__main__":
    main()
