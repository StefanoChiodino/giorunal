import os
from datetime import datetime
from os import listdir, remove
from os.path import isfile, join
from typing import List

import frontmatter as frontmatter
from git import Repo, InvalidGitRepositoryError, Remote, NoSuchPathError

from entry import Entry
from helpers.encryption import password_encrypt, password_decrypt
from helpers.filesystem import safe_make_dir_and_file, safe_make_dir
from helpers.keychain import get_password_from_keychain_with_fallback
from journal_configuration import JournalConfiguration, get_journal_configuration


class Journal(object):
    def __init__(self, journal_configuration: JournalConfiguration) -> None:
        self.journal_configuration: JournalConfiguration = journal_configuration

    def decrypt(self) -> None:
        """ Decrypt all entries in place. """
        self.git_sync()
        password: str = get_password_from_keychain_with_fallback()
        file_names: List[str] = self._all_entries_file_names()

        for file_name in file_names:
            encrypted_entry_filename = join(self.journal_configuration.journal_path, file_name)
            with open(encrypted_entry_filename, "rb") as encrypted_file:
                encrypted_entry: bytes = encrypted_file.readline()

            decrypted_entry: str = password_decrypt(encrypted_entry, password).decode()
            frontmatter_entry: frontmatter.Post = frontmatter.loads(decrypted_entry)

            with open(f"{encrypted_entry_filename}.md", "wb") as decrypted_file:
                frontmatter.dump(frontmatter_entry, decrypted_file)

            remove(encrypted_entry_filename)

    def encrypt(self) -> None:
        """ Encrypt all entries in place. """
        self.git_sync()
        password: str = get_password_from_keychain_with_fallback()
        file_names: List[str] = [f for f in self._all_entries_file_names() if f.endswith(".md")]

        for file_name in file_names:
            decrypted_entry_filename = join(self.journal_configuration.journal_path, file_name)
            with open(decrypted_entry_filename, "r") as decrypted_file:
                decrypted_frontmatter_entry: Post = frontmatter.load(decrypted_file)

            decrypted_entry: str = frontmatter.dumps(decrypted_frontmatter_entry)

            encrypted_formatted_entry: bytes = password_encrypt(
                decrypted_entry.encode(), password
            )
            filename = decrypted_frontmatter_entry["created"].strftime("%Y_%m_%d-%H_%M_%S")

            with open(os.path.join(self.journal_configuration.journal_path, filename), "ab") as file:
                file.write(encrypted_formatted_entry)

            remove(decrypted_entry_filename)


    def list_entries(self) -> str:
        """ Returns all formatted entries with created date and body. """
        self.git_sync()
        file_names: List[str] = self._all_entries_file_names()
        password: str = get_password_from_keychain_with_fallback()
        entries: str = ""
        for file_name in file_names:
            if file_name.endswith(".md"):
                with open(join(self.journal_configuration.journal_path, file_name), "r") as file:
                    post: frontmatter.Post = frontmatter.load(file)
            else:
                with open(join(self.journal_configuration.journal_path, file_name), "rb") as file:
                    encrypted_entry: bytes = file.readline()
                    decrypted: str = password_decrypt(encrypted_entry, password).decode()
                    post: frontmatter.Post = frontmatter.loads(decrypted)
            entries += f"{post.metadata['created']}: {post.content}\n\n"

        return entries

    def _all_entries_file_names(self):
        file_names: List[str] = [f for f in listdir(self.journal_configuration.journal_path) if
                                 isfile(join(self.journal_configuration.journal_path, f))
                                 and not f.startswith(".")]
        return file_names

    def git_sync(self) -> None:
        try:
            try:
                repo: Repo = Repo(self.journal_configuration.journal_path)
            except NoSuchPathError:
                safe_make_dir(self.journal_configuration.journal_path)
                repo: Repo = Repo(self.journal_configuration.journal_path)
        except InvalidGitRepositoryError:
            print("# Creating git repo")
            repo: Repo = Repo.init(self.journal_configuration.journal_path)
            if self.journal_configuration.sync_to_git:
                remote_url: str = input("Git remote not initialised, insert URL: ")
                origin: Remote = repo.create_remote("origin", remote_url)
                repo.heads.master.set_tracking_branch(repo.remotes.origin.refs.master)

        if self.journal_configuration.sync_to_git:
            repo.remotes.origin.pull()

        repo.index.add("*")
        if repo.is_dirty():
            repo.index.commit("update")
            if self.journal_configuration.sync_to_git:
                repo.remotes.origin.push("master")

    def add_entry(self, entry_body: str) -> None:
        self.git_sync()

        created: datetime = datetime.now()
        entry: Entry = Entry(body=entry_body, created=created, last_modified=created)

        formatted_entry: str = entry.to_frontmatter()

        password: str = get_password_from_keychain_with_fallback()
        encrypted_formatted_entry: bytes = password_encrypt(
            formatted_entry.encode(), password
        )
        filename = created.strftime("%Y_%m_%d-%H_%M_%S")

        with open(os.path.join(self.journal_configuration.journal_path, filename), "ab") as file:
            file.write(encrypted_formatted_entry)

        self.git_sync()


def initialise_journal(journal_path: str) -> None:
    print(f"Journal will be created at '{journal_path}'.")
    password: str

    safe_make_dir_and_file(journal_path)


def get_journal(config_path: str) -> Journal:
    journal_configuration: JournalConfiguration = get_journal_configuration(config_path)

    if not os.path.exists(journal_configuration.journal_path):
        initialise_journal(journal_configuration.journal_path)

    return Journal(journal_configuration)
