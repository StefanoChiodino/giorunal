import argparse
import os
import sys
from pathlib import Path
from typing import Callable, List
from json.decoder import JSONDecodeError

from journal_configuration import JournalConfiguration, initialise_journal_config
from journal import Journal, get_journal

CONFIG_PATH = f"{str(Path.home())}/.giournal"


def print_entries() -> None:
    journal: Journal = get_journal(CONFIG_PATH)
    entries: str = journal.list_entries()
    print(entries)


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


def main() -> None:
    try:
        journal_configuration: JournalConfiguration = JournalConfiguration.load(CONFIG_PATH)
    except (JSONDecodeError, FileNotFoundError) as _:
        initialise_journal_config(CONFIG_PATH)
        journal_configuration: JournalConfiguration = JournalConfiguration.load(CONFIG_PATH)

    args = _parse_args(sys.argv[1:])

    if isinstance(args.callable, Callable):
        args.callable()
    elif args.text:
        journal: Journal = Journal(journal_configuration)
        journal.add_entry(" ".join(args.text).strip())


if __name__ == "__main__":
    main()
