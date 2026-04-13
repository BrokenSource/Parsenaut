"""Note: Filename avoids collision, not a private module!"""
import itertools
import sys
from typing import Annotated, Any

from attrs import Factory, define
from cyclopts import App, Parameter

from parsenaut import BaseLauncher, Entry


@define
class Launcher(BaseLauncher):
    """Cyclopts-based launcher"""

    cli: App = Factory(lambda: App(
        version_flags=[],
        help_flags=[],
        usage="",
    ))

    @staticmethod
    def chain(app: App):
        """Implements known commands chaining in meta app"""
        def meta(*tokens: Annotated[str, Parameter(show=False, allow_leading_hyphen=True)]):
            if (splits := [n for (n, token) in enumerate(tokens) if token in app]):
                for start, end in itertools.pairwise(splits + [len(tokens)]):
                    app(tokens[start:end], result_action=app[tokens[start]].result_action)
                return None
            return app()
        app.meta.default(meta)

    def add(self, meta: Entry) -> None:

        # Note: Method definition works as a wrapper
        def runner(*args: Annotated[str, Parameter(
            allow_leading_hyphen=True,
            show=False,
        )]):
            self.run(meta, *args)

        self.cli.command(runner,
            name=meta.name.lower(),
            help=(meta.desc or "No description provided"),
            group=f"📦 {self.keyword}s at ({meta.path})",
        )

    def run(self, meta: Entry, *args: str) -> Any:
        """Assumes a chained .cli field in the class"""
        sys.argv[1:] = args
        instance = meta.cls()
        instance.cli.meta(args)
        return instance
