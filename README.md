# greqs

## Installation

```sh
pip install git+https://github.com/Dog-Egg/greqs.git
```

## Usage

```sh
greqs -h
```


**greqs** can only recognize `from ... import ...` or `import ...` statements.
For implicitly imported packages or packages imported in other ways, you can annotate them in the code using the `# requirements: <package1> <package2> ...` comment.

For example:

```python
# requirements: psycopg[binary] lxml
```
