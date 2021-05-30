import os
from datetime import datetime
from pathlib import Path
from typing import List

from git import Repo, InvalidGitRepositoryError, Remote

from entry import Entry
from helpers.encryption import password_encrypt, password_decrypt


class Journal(object):
    def __init__(self, path: str, password: str):
        self.password: str = password
        self.path: str = path

    def list_entries(self) -> str:
        self.git_sync()
        with open(self.path, "rb") as file:
            encrypted_entries: List[bytes] = file.readlines()

        decrypted: List[str] = [password_decrypt(encrypted_entry, self.password).decode() for encrypted_entry in
                                encrypted_entries]
        return os.linesep.join(decrypted)

    def format_entry(self, entry: Entry) -> str:
        # TODO: UTC? Timezone?
        return f"[{entry.created}{f'<{entry.last_modified}>' if entry.last_modified != entry.created else ''}]{entry.body}"

    def git_sync(self) -> None:
        path = Path(self.path)
        try:
            repo: Repo = Repo(path.parent)
        except InvalidGitRepositoryError:
            print("# Creating git repo")
            repo: Repo = Repo.init(path.parent)
            remote_url: str = input("Git remote not initialised, insert URL: ")
            origin: Remote = repo.create_remote("origin", remote_url)
            repo.index.add([path])
            repo.index.commit("init")
            origin.push("master")
            repo.heads.master.set_tracking_branch(repo.remotes.origin.refs.master)

        repo.remotes.origin.pull()

        if repo.is_dirty():
            repo.index.add([JOURNAL_FILENAME])
            repo.index.commit("update")
            repo.remotes.origin.push("master")

    def add_entry(self, entry_body: str) -> None:
        self.git_sync()

        created: datetime = datetime.now()
        entry: Entry = Entry(created, created, entry_body)

        formatted_entry: str = self.format_entry(entry)

        encrypted_formatted_entry: bytes = password_encrypt(formatted_entry.encode(), self.password)

        with open(self.path, "ab") as file:
            file.write(os.linesep.encode() + encrypted_formatted_entry)

        self.git_sync()
