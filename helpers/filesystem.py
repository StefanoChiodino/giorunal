import os
from pathlib import Path


def safe_make_dir_and_file(file_path: str) -> None:
    journal_path: Path = Path(file_path)
    if not os.path.exists(journal_path.parent):
        os.mkdir(journal_path.parent)
    if not os.path.exists(journal_path):
        open(journal_path, "a").close()
