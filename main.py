""" Based on https://stackoverflow.com/questions/2490334/simple-way-to-encode-a-string-according-to-a-password """
import argparse
import os
import secrets
from datetime import datetime
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from pathlib import Path
from typing import List, Optional, Callable

from cryptography.fernet import Fernet

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from helpers.keychain import get_password_from_keychain, get_password_from_keychain_with_fallback

ITERATIONS = 100000


# ENCODING = "utf-8"


def _derive_key(password: bytes, salt: bytes, iterations: int = ITERATIONS) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=default_backend())
    return b64e(kdf.derive(password))


def password_encrypt(message: bytes, password: str, iterations: int = ITERATIONS) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def password_decrypt(token: bytes, password: str) -> bytes:
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)


#
# journal_folder_path = f"{str(Path.home())}/giournal"
#
# key = Fernet.generate_key()
#
# password = getpass.getpass(stream=None)
#
# if not os.path.isdir(journal_folder_path):
#     os.mkdir(journal_folder_path)
#
# with open(journal_path, "rb") as file:
#     data = file.read()
#     decrypted = password_decrypt(data, password)
#
#
# with tempfile.NamedTemporaryFile(suffix="md") as temp_file:
#     subprocess.call(["code", "-w", temp_file.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     entry: str = f"{decrypted}{os.linesep}{datetime.utcnow()}{os.linesep}{temp_file.read()}{os.linesep}"
#     encrypted: bytes = password_encrypt(entry.encode(), password)
#     # TODO: delete tmp file?
#
# with open(journal_path, 'wb') as file:
#     file.write(encrypted)


class Entry(object):
    def __init__(self, created: datetime, last_modified: datetime, body: str) -> None:
        self.body: str = body
        self.last_modified: datetime = last_modified
        self.created: datetime = created


class Journal(object):
    def __init__(self, path: str, password: str):
        self.password: str = password
        self.path: str = path
        # self.entries: Optional[List[Entry]] = None

    def list_entries(self) -> str:
        with open(self.path, "rb") as file:
            encrypted_entries: List[bytes] = file.readlines()

        decrypted: List[str] = [password_decrypt(encrypted_entry, self.password).decode() for encrypted_entry in
                                encrypted_entries]
        return os.linesep.join(decrypted)

    def format_entry(self, entry: Entry) -> str:
        # TODO: UTC? Timezone?
        return f"[{entry.created}{f'<{entry.last_modified}>' if entry.last_modified != entry.created else ''}]{entry.body}"

    def add_entry(self, entry_body: str) -> None:
        created: datetime = datetime.now()
        entry: Entry = Entry(created, created, entry_body)

        # if self.entries:
        #     self.entries += [entry_body]

        formatted_entry: str = self.format_entry(entry)

        encrypted_formatted_entry: bytes = password_encrypt(formatted_entry.encode(), self.password)

        with open(self.path, "wb") as file:
            file.writelines([encrypted_formatted_entry])


def get_journal() -> Journal:
    password = get_password_from_keychain_with_fallback()
    return Journal(f"{str(Path.home())}/journal", password)


def print_entries() -> None:
    journal: Journal = get_journal()
    entries: str = journal.list_entries()
    print(entries)


def main() -> None:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--list",
        action="store_const",
        const=print_entries,
        dest="callable",
        help="lists all the entries")

    argument_parser.add_argument("text", metavar="", nargs="*")

    args: argparse.Namespace = argument_parser.parse_args()

    if isinstance(args.callable, Callable):
        args.callable()
    elif args.text:
        journal: Journal = get_journal()
        journal.add_entry(args.text[0])


if __name__ == "__main__":
    main()
