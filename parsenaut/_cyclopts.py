"""Note: Filename avoids collision, not a private module!"""

import itertools
import sys
from typing import Annotated, Callable
import runpy

from cyclopts import App, Parameter
from attrs import Factory, define

from parsenaut import BaseLauncher, iClass

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

@define
class Launcher(BaseLauncher):
    cli: App = Factory(lambda: App(
        version_flags=[],
        help_flags=[],
        usage="",
    ))

    def wrapper(self, meta: iClass) -> Callable:
        def run(*args: Annotated[str, Parameter(
            allow_leading_hyphen=True,
            show=False,
        )]):
            module = runpy.run_path(str(meta.script))
            app = module[meta.name]
            sys.argv[1:] = args
            self.run(app)
        return run

    def add(self, meta: iClass):
        self.cli.command(
            self.wrapper(meta),
            name=meta.name.lower(),
            help=(meta.docstring or "No description provided"),
            group=f"📦 {self.tag}s at ({meta.script})",
        )

    def run(self, object, *args):
        object.cli.meta(args)
