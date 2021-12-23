from datetime import datetime
from typing import Dict, Any

import frontmatter
from dataclasses import dataclass

@dataclass
class Entry(object):
    body: str
    last_modified: datetime
    created: datetime

    def to_frontmatter(self) -> str:
        entry_frontmatter: Dict["str", Any] = self.__dict__.copy()
        del entry_frontmatter["body"]
        post: frontmatter.Post = frontmatter.Post(self.body, **entry_frontmatter)
        return frontmatter.dumps(post)
