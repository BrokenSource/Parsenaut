A small package for parsing and launching classes from scripts as cli entries.

## Description

Scene-like apps may have a structure similar to:

```python
from package import Project

class Introduction(Project):
    ...

class Development(Project):
    ...
```

<sup><b>Examples:</b> [ShaderFlow](https://github.com/BrokenSource/ShaderFlow) • [Manim](https://github.com/ManimCommunity/manim)</sup>

Where usage may be:

```bash
$ package introduction (args)
```

...
