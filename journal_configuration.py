from __future__ import annotations

import dataclasses
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Dict, Any
import json

from helpers.filesystem import safe_make_dir_and_file


@dataclass
class JournalConfiguration:
    journal_path: str
    sync_to_git: bool
    git_remote: str
    use_keychain: bool

    @classmethod
    def load(cls, path: str) -> JournalConfiguration:
        with open(path, "r") as file:
            loaded_dictionary: Dict[str, Any] = json.load(file)
            return cls(loaded_dictionary["journal_path"],
                       loaded_dictionary["sync_to_git"],
                       loaded_dictionary["git_remote"],
                       loaded_dictionary["use_keychain"],
                       )

    def store(self, path: str) -> None:
        with open(path, "w") as file:
            file.write(json.dumps(dataclasses.asdict(self)))


def get_journal_configuration(path: str) -> JournalConfiguration:
    if not os.path.exists(path):
        initialise_journal_config(path)
    journal_configuration: JournalConfiguration = JournalConfiguration.load(path)
    return journal_configuration


def initialise_journal_config(config_path) -> JournalConfiguration:
    def _parse_true_false(input: str, default: bool) -> bool:
        if input.lower() in ["true", "yes"]:
            return True
        if input.lower() in ["false", "no"]:
            return False
        return default

    print(f"# Creating journal config at '{config_path}'")
    default_journal_path: str = f"{str(Path.home())}/journal"
    journal_path = (
            input(f"Journal path [{default_journal_path}]: ") or default_journal_path
    )
    # print(f" WARNING: path '{journal_path}', already exists")
    if not os.path.exists(journal_path):
        print(f"Creating path '{journal_path}'")
        os.mkdir(journal_path)

    default_use_keychain: bool = True
    use_keychain: str = input(f"Do you want to store your password to your keychain? [{default_use_keychain}]: ")
    default_sync_to_git: bool = True
    sync_to_git: str = input(f"Do you want to sync your journal to git? [{default_sync_to_git}]: ")

    sync_to_git_bool: bool = _parse_true_false(sync_to_git, default_sync_to_git)
    git_remote: Optional[str] = input(f"What is your git remote? [e.g. git@github.com:username/repository.git] : ") \
        if sync_to_git_bool else None

    safe_make_dir_and_file(config_path)
    journal_config: JournalConfiguration = JournalConfiguration(
        journal_path=journal_path,
        use_keychain=_parse_true_false(use_keychain, default_use_keychain),
        sync_to_git=sync_to_git_bool,
        git_remote=git_remote,
    )
    journal_config.store(config_path)
    return journal_config
