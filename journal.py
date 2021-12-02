import json
import os
from datetime import datetime
from pathlib import Path
from sys import path
from typing import List
from uuid import uuid4

from git import Repo, InvalidGitRepositoryError, Remote

from entry import Entry
from helpers.encryption import password_encrypt, password_decrypt
from helpers.keychain import get_password_from_keychain_with_fallback, get_password_from_keychain
from journal_configuration import JournalConfiguration, get_journal_configuration
from helpers.filesystem import safe_make_dir_and_file


class Journal(object):
    def __init__(self, journal_configuration: JournalConfiguration) -> None:
        self.journal_configuration: JournalConfiguration = journal_configuration

    def list_entries(self) -> str:
        self.git_sync()
        with open(self.journal_configuration.journal_path, "rb") as file:
            encrypted_entries: List[bytes] = file.readlines()

        password: str = get_password_from_keychain_with_fallback()
        decrypted: List[str] = [
            password_decrypt(encrypted_entry, password).decode()
            for encrypted_entry in encrypted_entries
        ]
        return os.linesep.join(decrypted)

    def format_entry(self, entry: Entry) -> str:
        return json.dumps(entry.__dict__, default=str)

    def git_sync(self) -> None:
        try:
            repo: Repo = Repo(self.journal_configuration.journal_path)
        except InvalidGitRepositoryError:
            print("# Creating git repo")
            repo: Repo = Repo.init(self.journal_configuration.journal_path)
            repo.index.add([path])
            repo.index.commit("init")
            if self.journal_configuration.sync_to_git:
                remote_url: str = input("Git remote not initialised, insert URL: ")
                origin: Remote = repo.create_remote("origin", remote_url)
                origin.push("master")
            repo.heads.master.set_tracking_branch(repo.remotes.origin.refs.master)

        if self.journal_configuration.sync_to_git:
            repo.remotes.origin.pull()

        if repo.is_dirty():
            repo.index.add(".")
            repo.index.commit("update")
            repo.remotes.origin.push("master")

    def add_entry(self, entry_body: str) -> None:
        self.git_sync()

        created: datetime = datetime.now()
        entry: Entry = Entry(created, created, entry_body)

        formatted_entry: str = self.format_entry(entry)

        password: str = get_password_from_keychain_with_fallback()
        encrypted_formatted_entry: bytes = password_encrypt(
            formatted_entry.encode(), password
        )
        filename = str(uuid4())

        with open(os.path.join(self.journal_configuration.journal_path, filename), "ab") as file:
            file.write(os.linesep.encode() + encrypted_formatted_entry)

        self.git_sync()


def initialise_journal(journal_path: str) -> None:
    print(f"Journal will be created at '{journal_path}'.")
    password: str

    safe_make_dir_and_file(journal_path)


def get_journal(config_path: str) -> Journal:
    journal_configuration: JournalConfiguration = get_journal_configuration(config_path)

    if not os.path.exists(journal_configuration.journal_path):
        initialise_journal(journal_configuration.journal_path)

    return Journal(str(journal_configuration.journal_path))
