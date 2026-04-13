import re
import runpy
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from attrs import define

__all__ = [
    "BaseLauncher",
    "Entry",
]

@define
class Entry:
    """Information about a runnable class"""
    path: Path
    name: str
    desc: Optional[str]

    @property
    def module(self) -> dict:
        """Warning: Executes script as a module"""
        return runpy.run_path(str(self.path))

    @property
    def cls(self) -> type:
        return self.module[self.name]

@define
class BaseLauncher(ABC):
    """
    Abstract base class, default implementations, and common methods used
    in parsenaut launchers they follow and implements.
    """

    keyword: str
    """Substring to search for in class inheritance"""

    # -------------------------------- #
    # Default methods

    @property
    def pattern(self) -> re.Pattern:
        """
        Get a regex pattern with match groups:
        1. Class names with 'self.keyword' in inheritance
        2. Immediate optional triple-quoted docstring
        """
        return re.compile(''.join((
            r"^class\s+(\w+)\s"
            r"*\(.*?(?:" + self.keyword + r").*\):",
            r"\s*(?:\"\"\"((?:\n|.)*?)\"\"\")?",
        )), re.MULTILINE)

    def search(self, /, script: Path) -> bool:
        """Search for classes in given script or directory"""
        script: Path = Path(script)

        # Fixme: Regex or ast parsing?
        code: str = script.read_text(encoding="utf-8")
        matches = list(self.pattern.finditer(code))

        for match in matches:
            self.add(Entry(
                path=script,
                name=match.group(1),
                desc=match.group(2),
            ))

        return bool(matches)

    def smart(self,
        package: Path,
        directories: list = [
            "../projects",
            "../examples",
            "resources/examples",
        ],
    ) -> int:

        # Search current directory return early on matches
        if local := sum(map(self.search, Path.cwd().glob("*.py"))):
            return local

        search: list[Path] = list()
        package = Path(package)

        # Common places for repository
        for target in directories:
            path = package.joinpath(target).resolve()
            search.extend(path.rglob("*.py"))

        # Search and count total matches
        return sum(map(self.search, search))

    # -------------------------------- #
    # Abstract methods

    @abstractmethod
    def add(self, meta: Entry) -> None:
        """Add a new command to the launcher"""
        ...

    @abstractmethod
    def run(self, meta: Entry, *args: str) -> Any:
        """Instantiate and run entry with arguments"""
        ...

    # -------------------------------- #
    # Composite methods
