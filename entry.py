from datetime import datetime


class Entry(object):
    def __init__(self, created: datetime, last_modified: datetime, body: str) -> None:
        self.body: str = body
        self.last_modified: datetime = last_modified
        self.created: datetime = created
