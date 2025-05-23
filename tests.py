import sys

import pytest
from greqs import main
from greqs.helper import iter_import_modules
from inspect import cleandoc

sys.path.insert(0, "example")


def test_mod1():
    assert main("mod1") == [
        "Flask==3.0.3",
        "git+https://github.com/Dog-Egg/Zangar",
        "git+https://github.com/Dog-Egg/oasis.git#subdirectory=packages/flask-oasis",
        "lxml",
        "psycopg[binary]",
        "requests",
        "six",
    ]


def test_pkg1():
    assert main("pkg1") == ["requests", "six"]


def test_pkg2():
    assert main("pkg2") == ["admin-deps"]


def test_mod_err():
    with pytest.raises(ModuleNotFoundError) as e:
        main("mod_err")
    assert e.value.msg == "No module named 'validators'"


def test_cli():
    # 测试命令行
    from greqs import cli

    cli.main(["--verbose", "mod1"])


def test_iter_import_modules():
    assert (
        list(
            iter_import_modules(
                cleandoc(
                    """
        import os
        from . import utils
        from .tools import translations
        from otherpkg import *
    """
                ),
                "package.module",
            )
        )
        == [
            "os",
            "package",
            "package.module",
            "package.module.utils",
            "package.tools",
            "package.tools.translations",
            "otherpkg",
        ]
    )
