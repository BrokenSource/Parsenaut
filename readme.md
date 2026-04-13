<div align="center">
  <h1>Parsenaut</h1>
  <span>🚀 Parse and launch classes as commands 🚀</span>
</div>

## 📦 Description

Scene-like applications may use inheritance for multiple user-defined classes in local scripts, lacking dynamic entry points and/or needing a path and class name to run. Whether your project looks something like:

```python
from myproject import Scene


class Mandelbrot(Scene):
    """Mandelbrot example"""
    ...

class BurningShip(Scene):
    """Burning Ship example"""
    ...
```

One might want its usage to follow as:

```bash
# Lists all classes
$ myproject --help

📦 Scenes at (/home/user/scenes.py)
• mandelbrot      Mandelbrot example
• burningship     Burning Ship example

# Runs Mandelbrot().cli(*args)
$ myproject mandelbrot (args)
```

Parsenaut is a safe library for it that:

- **No exec**: Files are parsed with regex or abstract syntax trees and are never executed, saving import times and minimizing security issues in potentially untrusted scripts (non-greedy).
- **Compatible**: Works with [Cyclopts](https://pypi.org/project/cyclopts) or [Typer](https://pypi.org/project/typer/) command line libraries, at your taste.
- **Flexible**: Customizable class tags search, extensible classes.
- **Fast**: Does not spawn a subproces, uses stdlib [`runpy`](https://docs.python.org/3/library/runpy.html)

## 📦 Installation

Simply add the [`parsenaut`](https://pypi.org/project/parsenaut/) package in your `pyproject.toml`:

```toml
[project]
dependencies = ["parsenaut"]
```

## 📦 Usage

```python
# myproject/__main__.py
import sys
from pathlib import Path

from parsenaut._cyclopts import Launcher

if __name__ == "__main__":
    launcher = Launcher(keyword="Scene")

    for file in Path.cwd().glob("*.py"):
        launcher.search(file)

    launcher.cli(sys.argv[1:])
```
