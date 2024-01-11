"""Tools to analyze local code files for packages.

Note: Assumes these packages are in the format:

    package/  # aka project root
        setup.py
        setup.cfg
        README.md
        package/  # aka package directory
            __init__.py
            module1.py
            module2.py
            ...
"""

from functools import lru_cache
from dol import filt_iter, wrap_kvs, Pipe, cache_iter
from dol.filesys import FileCollection
from pathlib import Path
from dol.filesys import DirCollection


def dir_whose_parent_has_same_name(k):
    path = Path(k)
    return path.is_dir() and path.parent.name == path.name


def folder_has_init(path):
    return (Path(path) / '__init__.py').is_file()


def package_directory_of_project_root(path):
    path = Path(path)
    return str(path / path.name)


def is_project_root(path):
    path = Path(path)
    code_root = package_directory_of_project_root(path)
    return folder_has_init(code_root) and (path / 'setup.cfg').is_file()


def is_package_directory(path):
    path = Path(path)
    return folder_has_init(path)


# TODO: package_root_dirs and root_dirpaths_to_packages were writte before
#  is_package_directory and is_project_root, so refactor might be in order
def package_root_dirs(rootdir, max_levels=None, only_if_has_init=False):
    if only_if_has_init:
        init_filt = filt_iter(filt=lambda p: (Path(p) / '__init__.py').is_file())
    else:
        init_filt = lambda x: x
    S = Pipe(
        filt_iter(DirCollection, filt=dir_whose_parent_has_same_name),
        init_filt,
        wrap_kvs(
            key_of_id=lambda x: str(Path(x).parent),
            id_of_key=lambda x: str(Path(x) / Path(x).name),
        ),
        cache_iter,
    )
    return S(rootdir, max_levels=max_levels)


@lru_cache
def root_dirpaths_to_packages(rootdir, max_levels=None, only_if_has_init=False):
    return list(
        package_root_dirs(rootdir, max_levels, only_if_has_init=only_if_has_init)
    )


Packages = package_root_dirs  # backcomp alias


def init_root(init_filepath):
    return str(Path(init_filepath).parent)


def pkg_root(init_filepath):
    return str(Path(init_filepath).parent.parent)


def init_file_of_pkg_root(root):
    p = Path(root)
    return str(p / p.name / '__init__.py')


def is_package_init(k):
    if not k.endswith('__init__.py'):
        return False
    path = Path(k)
    parent = path.parent
    grandparent = parent.parent
    return parent.name == grandparent.name and (grandparent / 'setup.py').is_file()
