from __future__ import annotations

import enum
import functools
from importlib.machinery import ModuleSpec
import importlib.util
import logging
import os
import pkgutil
import site
import sys
import tokenize
import typing

import importlib_metadata as metadata

from .helper import find_module_spec, iter_import_modules

__version__ = "0.2.2"

logger = logging.getLogger("greqs")


class ModuleDependencyExtractor:
    def __init__(self):
        self.__extracted_modules: set[str] = set()

    def extract(
        self, modulespec: ModuleSpec
    ) -> typing.Generator[ModuleSpec, None, None]:
        if modulespec.name in self.__extracted_modules:
            return
        self.__extracted_modules.add(modulespec.name)

        logger.debug("Parsing module: %s", modulespec.name)

        assert modulespec.origin is not None
        with open(modulespec.origin, "r", encoding="utf-8") as f:
            for name, definite_module in iter_import_modules(f.read(), modulespec):
                spec = find_module_spec(name, definite_module)
                if spec:
                    yield spec


def is_stdlib_module(modulespec: ModuleSpec):
    """判断是否是标准库模块"""

    # 标准库目录通常在 sys.base_prefix/lib/pythonX.Y/
    stdlib_dir = os.path.join(
        sys.base_prefix,
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    )
    stdlib_dir = os.path.abspath(stdlib_dir)

    assert modulespec.origin is not None
    module_path = os.path.abspath(modulespec.origin)

    return module_path.startswith(stdlib_dir)


def is_third_party_module(modulespec: ModuleSpec):
    assert modulespec.origin is not None

    # 获取模块的加载信息
    module_path = os.path.abspath(modulespec.origin)

    # 第三方库一般安装在 site-packages 路径中
    for site_dir in site.getsitepackages() + [site.getusersitepackages()]:
        if module_path.startswith(os.path.abspath(site_dir)):
            return True

    return False


def _cache(func):
    _cache_values = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        if key not in _cache_values:
            _cache_values[key] = func(*args, **kwargs)
        return _cache_values[key]

    return wrapper


@_cache
def file_to_dist():
    rv: dict[str, metadata.Distribution] = {}
    for dist in metadata.distributions():
        for file in dist.files or []:
            path = dist.locate_file(".").joinpath(file)
            file_path = os.path.realpath(path.__str__())
            rv[file_path] = dist
    return rv


def find_distribution(modulespec: ModuleSpec):
    assert modulespec.origin is not None
    module_path = os.path.realpath(modulespec.origin)
    return file_to_dist()[module_path]


class ModuleTypeEnum(enum.IntEnum):
    STDLIB = enum.auto()
    THIRD_PARTY = enum.auto()
    LOCAL = enum.auto()


def walk_module(
    spec: ModuleSpec,
    dependency_extractor: ModuleDependencyExtractor | None = None,
) -> typing.Generator[tuple[ModuleTypeEnum, ModuleSpec], None, None]:
    if dependency_extractor is None:
        dependency_extractor = ModuleDependencyExtractor()

    if not spec.has_location:
        return

    if is_stdlib_module(spec):
        yield (ModuleTypeEnum.STDLIB, spec)
        return

    if is_third_party_module(spec):
        yield (ModuleTypeEnum.THIRD_PARTY, spec)
        return

    yield (ModuleTypeEnum.LOCAL, spec)

    # 递归遍历本地模块
    for s in dependency_extractor.extract(spec):
        yield from walk_module(s, dependency_extractor)


def get_submodules_specs(package_spec: ModuleSpec):
    assert package_spec.submodule_search_locations is not None
    specs: list[ModuleSpec] = [package_spec]  # 包含 __init__.py
    for location in package_spec.submodule_search_locations:
        # 遍历包目录中的模块和子包
        for module_info in pkgutil.walk_packages(
            [location], prefix=package_spec.name + "."
        ):
            sub_spec = importlib.util.find_spec(module_info.name)
            if sub_spec:
                specs.append(sub_spec)
    return specs


def extract_requirements_from_comments(file: str) -> typing.Generator[str]:
    comment_prefix = "# requirements:"

    with open(file, "r") as f:
        tokens = tokenize.generate_tokens(f.readline)
        for tok_type, tok_string, *_ in tokens:
            if tok_type != tokenize.COMMENT:
                continue
            if tok_string.startswith(comment_prefix):
                reqs = tok_string[len(comment_prefix) :]
                for req in reqs.split():
                    yield req


def get_reqs(spec: ModuleSpec):
    dists: list[metadata.Distribution] = []

    for model_type, spec in walk_module(spec):
        if model_type == ModuleTypeEnum.THIRD_PARTY:
            dists.append(find_distribution(spec))
        elif model_type == ModuleTypeEnum.LOCAL:
            assert spec.origin is not None
            yield from extract_requirements_from_comments(spec.origin)

    for dist in dists:
        origin = dist.origin
        if origin is not None and hasattr(origin, "vcs_info"):
            req = f"{origin.vcs_info.vcs}+{origin.url}"
            # req += f"@{origin.vcs_info.commit_id}" # FIXME commit_id 可能会导致依赖冲突，占时不加
            if hasattr(origin, "subdirectory"):
                req += f"#subdirectory={origin.subdirectory}"
        else:
            req = f"{dist.name}=={dist.version}"
        yield req


def _iter_specs(module: str):
    spec = importlib.util.find_spec(module)
    if spec is None:
        raise ModuleNotFoundError(f"Module {module!r} not found")

    if spec.submodule_search_locations is not None:
        # this is a package
        for s in get_submodules_specs(spec):
            yield s
    else:
        # just a module
        yield spec


def main(modules: list[str]) -> list[str]:
    reqs = set()
    for module in set(modules):
        # TODO 可能的重复执行待优化
        for spec in _iter_specs(module):
            for req in get_reqs(spec):
                reqs.add(req)

    return sorted(reqs)
