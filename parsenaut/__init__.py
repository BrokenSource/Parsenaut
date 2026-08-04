import ast
import runpy
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from attrs import define

__about__   = "🚀 Parse and launch classes as commands"
__package__ = "parsenaut"
__version__ = "0.2.1"
__license__ = "MIT"

@define
class Entry:
    """Information about a runnable class"""
    path: Path
    node: ast.ClassDef

    @property
    def name(self) -> str:
        """Get the name of the class from AST"""
        return self.node.name

    @property
    def docstring(self) -> str | None:
        """Get the docstring of the class from AST"""
        return ast.get_docstring(self.node)

    @property
    def module(self) -> dict:
        """Runs the script and returns its globals"""
        return runpy.run_path(str(self.path))

    @property
    def cls(self) -> type:
        """Run the script and get the target class"""
        return self.module[self.name]

SEARCH: list[str] = [
    "../projects",
    "../examples",
    "examples",
    "resources/examples",
]

@define
class BaseLauncher(ABC):
    """
    Abstract base class, default implementations, and common methods used
    in parsenaut launchers they follow and implements.
    """

    keyword: str
    """Substring to search for in class inheritance"""

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
    # Default methods

    def search(self, /, script: Path) -> int:
        """Search for classes containing keyword, returns total matches"""
        script = Path(script)
        matches: int = 0

        # Speed: Only look for root nodes in body
        for node in ast.parse(
            script.read_text(encoding="utf-8"),
            filename=str(script),
        ).body:

            # Only look for class definitions
            if not isinstance(node, ast.ClassDef):
                continue

            # Keyword must be in the string name of base classes
            if any(self.keyword in base.id for base in node.bases): # type: ignore
                self.add(Entry(path=script, node=node))
                matches += 1

        return matches

    def smart(self,
        package: Path,
        directories: list=SEARCH,
    ) -> int:

        # Search current directory return early on matches
        if local := sum(map(self.search, Path.cwd().glob("*.py"))):
            return local

        search: list[Path] = []
        package = Path(package)

        # Common places for repository
        for target in directories:
            path = package.joinpath(target).resolve()
            search.extend(path.rglob("*.py"))

        # Search and count total matches
        return sum(map(self.search, search))
