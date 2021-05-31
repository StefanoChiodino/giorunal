from __future__ import annotations
from typing import Optional, Union, Dict, Any
import json


class JournalConfiguration:
    def __init__(
        self,
        file_path: Optional[str] = None,
        sync_to_git: Optional[bool] = None,
        use_keychain: Optional[bool] = None,
    ) -> None:
        self.use_keychain: Optional[bool] = use_keychain
        self.sync_to_git: Optional[bool] = sync_to_git
        self.journal_path: Optional[str] = file_path

    def store(self, path: str) -> None:
        with open(path, "w") as file:
            file.write(json.dumps(self.__dict__))

    def load(self, path: str) -> JournalConfiguration:
        with open(path, "r") as file:
            self.__dict__ = json.load(file)
        return self
