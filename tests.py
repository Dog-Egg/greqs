import sys

import pytest
from greqs import main

sys.path.insert(0, "example")


def test_mod1():
    assert main("mod1") == [
        "Flask==3.0.3",
        "git+https://github.com/Dog-Egg/Zangar",
        "git+https://github.com/Dog-Egg/oasis.git#subdirectory=packages/flask-oasis",
        "lxml",
        "psycopg[binary]",
        "requests",
    ]


def test_pkg1():
    assert main("pkg1") == [
        "requests",
    ]


def test_mod_err():
    with pytest.raises(ModuleNotFoundError) as e:
        main("mod_err")
    assert e.value.msg == "No module named 'validators'"


def test_cli():
    # 测试命令行
    from greqs import cli
    import sys

    sys.argv = ["greqs", "mod1"]
    cli.main()
