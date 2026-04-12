import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional

from attrs import define

__all__ = [
    "BaseLauncher",
    "iClass",
]

@define
class iClass:
    """Information about a runnable class"""
    script: Path
    name: str
    docstring: Optional[str]

@define
class BaseLauncher(ABC):

    tag: str
    """Substring to search for in class inheritance"""

    @property
    def pattern(self) -> re.Pattern:
        """
        Get a regex pattern with match groups:
        1. Class names with 'self.tag' in inheritance string
        2. Immediate optional triple-quoted docstring
        """
        return re.compile(''.join((
            r"^class\s+(\w+)\s"
            r"*\(.*?(?:" + self.tag + r").*\):",
            r"\s*(?:\"\"\"((?:\n|.)*?)\"\"\")?",
        )), re.MULTILINE)

    def search(self, script: Path):
        for match in self.pattern.finditer(script.read_text()):
            self.add(iClass(
                script=script,
                name=match.group(1),
                docstring=match.group(2),
            ))

    @abstractmethod
    def wrapper(self, meta: iClass) -> Callable:
        """Get a runnable"""
        ...

    @abstractmethod
    def add(self, meta: iClass):
        ...

    @abstractmethod
    def run(self, object: Any, *args: str):
        ...

    def common(self, package: Path) -> None:
        """
        Heuristic for searching common locations:
        - Standalone mode: local directory
        """
        search = list()

        # Search all local files
        search.extend(Path.cwd().glob("*.py"))

        # Only scan local files when found
        if sum(map(self.search, search)):
            return None

        search.clear()

        # Search repository examples or projects
        if (package := Path(package)).exists():
            search.extend((package.parent/"examples").rglob("*.py"))
            search.extend((package.parent/"projects").rglob("*.py"))

        # Search bundled examples
        search.extend((package/"resources").rglob("*.py"))

        for path in search:
            self.search(path)
