import json
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass
class AppItem:
    name: str
    path: str
    args: str = ""
    is_browser: bool = False
    urls: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.urls is None:
            self.urls = []
        # Fix path separators
        if self.path:
            self.path = self.path.replace("/", "\\").strip()
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Profile:
    name: str
    filename: str
    items: List[AppItem]
    delay: int = 1
    single_browser_window: bool = False
    run_as_admin: bool = False
    
    def to_dict(self):
        return {
            "name": self.name,
            "filename": self.filename,
            "items": [item.to_dict() for item in self.items],
            "delay": self.delay,
            "single_browser_window": self.single_browser_window,
            "run_as_admin": self.run_as_admin
        }
    
    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        items = [AppItem(**item) for item in data.pop('items', [])]
        return cls(items=items, **data)