from __future__ import annotations

import ast
import importlib.util
import typing


def _iter_import_modules(code: str, module: str) -> typing.Generator[str, None, None]:
    """
    从代码中获取可能的导入模块名 (有可能导入的是对象，但该函数不进行分辨)

    @param code: 模块代码
    @param module: 模块名
    """
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level == 0:
                assert node.module is not None
                parent_name = node.module
            else:
                name = "." * node.level
                if node.module:
                    name = name + "." + node.module
                parent_name = importlib.util.resolve_name(name, module)

            for n in node.names:
                if n.name == "*":
                    yield parent_name
                else:
                    yield f"{parent_name}.{n.name}"

        elif isinstance(node, ast.Import):
            for n in node.names:
                yield n.name


def iter_import_modules(*args, **kwargs) -> typing.Generator[str, None, None]:
    unique = set()
    for name in _iter_import_modules(*args, **kwargs):
        # 当导入一个 pkg.mod 的模块时，必然会导入 pkg.__init__ (也就是 pkg)，所以需要将模块名逐级展开。
        for n in _expand_module_name(name):
            if n not in unique:
                unique.add(n)
                yield n


def _expand_module_name(name: str) -> list[str]:
    parts = name.split(".")
    return [".".join(parts[: i + 1]) for i in range(len(parts))]
