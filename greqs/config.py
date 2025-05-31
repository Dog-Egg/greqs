import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_config() -> dict:
    # TODO: 验证 config。需要检查数据结构，检查不需要要的 key。
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        return {}
    return config.get("tool", {}).get("greqs", {})
