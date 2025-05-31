# greqs

Use the module as the entry point and track import statements to generate requirements.

## Installation

```sh
pip install git+https://github.com/Dog-Egg/greqs.git
```

## Usage

```
usage: greqs [-h] [--verbose] [--output FILE] module

Get requirements from a module (or a package)

positional arguments:
  module

options:
  -h, --help     show this help message and exit
  --verbose      enable verbose mode
  --output FILE  output the requirements to a file
```


**greqs** can only recognize `from ... import ...` or `import ...` statements.
For implicitly imported packages or packages imported in other ways, you can annotate them in the code using the `# requirements: <package1> <package2> ...` comment.

For example:

```python
# requirements: psycopg[binary] lxml
```

## Configuration

You can configure **greqs** by adding a `[tool.greqs]` section to your `pyproject.toml` file.

```toml
[tool.greqs]
ignore_version = ["flask"]
```

* `ignore_version`: a list of package names (case-insensitive) that should not have their version pinned. You can also set this to `true` to ignore the version of all packages.
