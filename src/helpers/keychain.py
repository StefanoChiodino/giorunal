import sys
from getpass import getpass
from typing import Optional

import keyring as keyring
from keyring.errors import KeyringError


def get_password_from_keychain_with_fallback() -> str:
    password: str = keyring.get_password("giournal", "giournal")
    if password is None:
        password: str = getpass("Configure a password: ")
        set_password_in_keychain(password)

    return password


def get_password_from_keychain() -> Optional[str]:
    try:
        return keyring.get_password("giournal", "giournal")
    except KeyringError as e:
        if not isinstance(e, keyring.errors.NoKeyringError):
            print("Failed to retrieve keyring", file=sys.stderr)
        return None


def set_password_in_keychain(password: Optional[str]) -> None:
    if password is None:
        try:
            keyring.delete_password("giournal", "giournal")
        except KeyringError:
            pass
    else:
        try:
            keyring.set_password("giournal", "giournal", password)
        except KeyringError as e:
            if isinstance(e, keyring.errors.NoKeyringError):
                print(
                    "Keyring backend not found. Please install one of the supported backends by visiting:"
                    " https://pypi.org/project/keyring/",
                    file=sys.stderr,
                )
            else:
                print("Failed to retrieve keyring", file=sys.stderr)
