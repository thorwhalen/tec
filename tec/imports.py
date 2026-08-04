"""Find the imports of python code, using the standard library's ``ast``.

This module answers the question *"what does this code import?"* by parsing the
code into an abstract syntax tree and walking it -- so, unlike the regex-based
:mod:`tec.import_counting`, it is not fooled by import-looking strings, comments,
or line continuations.

The simple thing is simple:

>>> [imp.name for imp in imports_in_code("import os\\nfrom json import dumps")]
['os', 'json.dumps']

The interface has three levels, from most to least specific:

- :func:`imports_in_code`: imports of a string of python code
- :func:`find_imports`: imports of a single ``.py`` file
- :func:`imports_under_folder` / :func:`count_imports`: imports of every ``.py``
  file under a folder -- reached through the :class:`~tec.stores.PyFilesReader`
  store, so a "folder" can also be a module object, a package, or the path of an
  ``__init__.py`` file

:class:`ModuleImports` offers the same information as a ``Mapping`` from module
dotpath to the imports of that module.

Note: this module replaces the vendored copy of the (GPL-2.0-or-later) third
party ``findimports`` project that ``tec`` used to ship as ``tec.findimports``.
It is an independent implementation, written against the standard library, so
that ``tec`` can be distributed under its own Apache-2.0 terms.

"""

from __future__ import annotations

import ast
import os
import warnings
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional, Union

from dol import KvReader

from tec.modules import py_path_to_dot_path
from tec.stores import PyFilesReader

#: Placeholder used as the ``filename`` of imports parsed from a code string.
CODE_STRING_FILENAME = "<string>"

#: Value of :attr:`ImportInfo.level` for an absolute (non-relative) import.
ABSOLUTE_IMPORT_LEVEL = 0


@dataclass(frozen=True)
class ImportInfo:
    """A single imported name, along with where it was found.

    >>> imp = ImportInfo("os.path", "a.py", 3)
    >>> imp.name, imp.lineno, imp.is_relative
    ('os.path', 3, False)

    Relative imports carry the number of leading dots in ``level``:

    >>> ImportInfo("sibling", "a.py", 1, level=1).is_relative
    True

    """

    #: Dotted name of what is imported (e.g. ``'os.path'``, ``'json.dumps'``).
    name: str
    #: File the import was found in (:data:`CODE_STRING_FILENAME` if unknown).
    filename: str = CODE_STRING_FILENAME
    #: 1-based line number of the ``import``/``from`` statement.
    lineno: int = 0
    #: Number of leading dots of a relative import (``0`` if absolute).
    level: int = ABSOLUTE_IMPORT_LEVEL

    @property
    def is_relative(self) -> bool:
        """True if, and only if, this is a relative (``from .x import y``) import."""
        return self.level > ABSOLUTE_IMPORT_LEVEL


def base_package_of(imp: Union[ImportInfo, str]) -> str:
    """The top-level package name of an import (``''`` for relative imports).

    >>> base_package_of("collections.abc")
    'collections'
    >>> base_package_of(ImportInfo("os.path"))
    'os'

    A relative import has no resolvable top-level package, so it maps to ``''``:

    >>> base_package_of(ImportInfo("sibling", level=1))
    ''

    """
    if isinstance(imp, ImportInfo):
        if imp.is_relative:
            return ""
        imp = imp.name
    return imp.partition(".")[0]


def raise_parse_error(error: SyntaxError, path: str) -> None:
    """``on_parse_error`` strategy: let the ``SyntaxError`` propagate."""
    raise error


def warn_of_parse_error(error: SyntaxError, path: str) -> None:
    """``on_parse_error`` strategy: warn about the file, then skip it."""
    warnings.warn(f"Skipping {path}: couldn't parse it: {error}", stacklevel=2)


def ignore_parse_error(error: SyntaxError, path: str) -> None:
    """``on_parse_error`` strategy: silently skip the file."""


#: Default aggregation key of :func:`count_imports`: the top-level package name.
DFLT_IMPORT_KEY = base_package_of

#: Default file-path predicate: ``None``, i.e. no filtering beyond the store's own
#: restriction to ``.py`` files.
DFLT_PATH_FILT = None

#: Default reaction to a file that can't be parsed while walking a folder. Folders
#: of real-world code routinely contain a stray py2 (or templated) file, so the
#: default is to warn and move on instead of aborting the whole walk.
DFLT_ON_PARSE_ERROR = warn_of_parse_error


def _import_infos_of_node(node: ast.AST, filename: str) -> Iterator[ImportInfo]:
    """Yield the :class:`ImportInfo` of a single ast node (nothing if not an import)."""
    if isinstance(node, ast.Import):
        for alias in node.names:
            yield ImportInfo(alias.name, filename, node.lineno)
    elif isinstance(node, ast.ImportFrom):
        prefix = f"{node.module}." if node.module else ""
        for alias in node.names:
            yield ImportInfo(
                f"{prefix}{alias.name}",
                filename,
                node.lineno,
                level=node.level or ABSOLUTE_IMPORT_LEVEL,
            )


def imports_in_code(
    code: str, *, filename: str = CODE_STRING_FILENAME
) -> Iterator[ImportInfo]:
    """Generate the :class:`ImportInfo` of every import found in ``code``.

    :param code: The python source to parse.
    :param filename: What to record as the origin of the imports found.
    :return: A generator of :class:`ImportInfo`.

    >>> code = '''
    ... import os, sys
    ... import os.path as osp
    ... from collections.abc import Mapping
    ... from . import sibling
    ... from ..pkg import thing
    ... '''
    >>> [imp.name for imp in imports_in_code(code)]
    ['os', 'sys', 'os.path', 'collections.abc.Mapping', 'sibling', 'pkg.thing']

    Unlike a regex-based scan, text that merely *looks* like an import is ignored:

    >>> list(imports_in_code('x = "import antigravity"  # import antigravity'))
    []

    Imports nested in functions, classes, ``try`` blocks etc. are included:

    >>> [imp.name for imp in imports_in_code("def f():\\n    import lazily\\n")]
    ['lazily']

    Code that doesn't parse raises a ``SyntaxError`` naming the offending file:

    >>> list(imports_in_code("import ;", filename="broken.py")
    ... )  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    SyntaxError: invalid syntax (broken.py, line 1)

    """
    tree = ast.parse(code, filename=filename)
    for node in ast.walk(tree):
        yield from _import_infos_of_node(node, filename)


def find_imports(filename: str) -> Iterator[ImportInfo]:
    """Generate the :class:`ImportInfo` of every import of the ``.py`` file ``filename``.

    :param filename: Path of the python file to parse.
    :return: A generator of :class:`ImportInfo`.

    >>> imports = list(find_imports(__file__))
    >>> "ast" in {imp.name for imp in imports}
    True
    >>> {imp.filename for imp in imports} == {__file__}
    True

    """
    with open(filename, encoding="utf-8") as fp:
        code = fp.read()
    yield from imports_in_code(code, filename=filename)


def imports_under_folder(
    src: Any,
    *,
    path_filt: Optional[Callable[[str], bool]] = DFLT_PATH_FILT,
    on_parse_error: Callable[[SyntaxError, str], None] = DFLT_ON_PARSE_ERROR,
) -> Iterator[ImportInfo]:
    """Generate the :class:`ImportInfo` of every ``.py`` file under ``src``.

    :param src: Anything :class:`~tec.stores.PyFilesReader` accepts: a folder path,
        a module or package object, or the path of an ``__init__.py`` file.
    :param path_filt: Optional predicate on the store's (relative) file paths, to
        narrow down the files that are parsed. ``None`` means "all ``.py`` files".
    :param on_parse_error: What to do with a file that doesn't parse. Called with
        the ``SyntaxError`` and the path. See :func:`raise_parse_error`,
        :func:`warn_of_parse_error` (the default) and :func:`ignore_parse_error`.
    :return: A generator of :class:`ImportInfo`.

    >>> import tempfile
    >>> from pathlib import Path
    >>> with tempfile.TemporaryDirectory() as root:
    ...     _ = Path(root, 'a.py').write_text('import os\\n')
    ...     _ = Path(root, 'b_test.py').write_text('import json\\n')
    ...     all_names = sorted(imp.name for imp in imports_under_folder(root))
    ...     kept = sorted(
    ...         imp.name
    ...         for imp in imports_under_folder(
    ...             root, path_filt=lambda p: not p.endswith('_test.py')
    ...         )
    ...     )
    >>> all_names
    ['json', 'os']
    >>> kept
    ['os']

    """
    store = PyFilesReader(src)
    for path, code in store.items():
        if path_filt is not None and not path_filt(path):
            continue
        try:
            imports = list(imports_in_code(code, filename=path))
        except SyntaxError as error:
            on_parse_error(error, path)
        else:
            yield from imports


def count_imports(
    src: Any,
    *,
    path_filt: Optional[Callable[[str], bool]] = DFLT_PATH_FILT,
    import_key: Callable[[ImportInfo], Any] = DFLT_IMPORT_KEY,
    on_parse_error: Callable[[SyntaxError, str], None] = DFLT_ON_PARSE_ERROR,
) -> Counter:
    """Count the imports of every ``.py`` file under ``src``.

    :param src: Anything :class:`~tec.stores.PyFilesReader` accepts (see
        :func:`imports_under_folder`).
    :param path_filt: Optional predicate on the store's (relative) file paths.
    :param import_key: What to count: applied to each :class:`ImportInfo`, it
        returns the value that is tallied. Defaults to :func:`base_package_of`,
        i.e. the top-level package name.
    :param on_parse_error: See :func:`imports_under_folder`.
    :return: A :class:`collections.Counter`.

    >>> import tempfile
    >>> from pathlib import Path
    >>> with tempfile.TemporaryDirectory() as root:
    ...     _ = Path(root, 'a.py').write_text('import os\\nfrom os import path\\n')
    ...     _ = Path(root, 'b.py').write_text('import os.path\\nimport json\\n')
    ...     counts = count_imports(root)
    ...     full = count_imports(root, import_key=lambda imp: imp.name)
    >>> sorted(counts.items())
    [('json', 1), ('os', 3)]
    >>> sorted(full.items())
    [('json', 1), ('os', 1), ('os.path', 2)]

    """
    return Counter(
        import_key(imp)
        for imp in imports_under_folder(
            src, path_filt=path_filt, on_parse_error=on_parse_error
        )
    )


#: Path separator that is legal but not native on this platform (``'/'`` on Windows,
#: ``None`` elsewhere). File stores are not required to use the native one.
FOREIGN_PATH_SEP = os.path.altsep


def _dotpath_of_py_path(py_path: str, root_module_str: str = "") -> str:
    """Module dotpath of a relative ``.py`` path (no leading dot when unrooted).

    >>> import os
    >>> _dotpath_of_py_path(os.path.join('a', 'b.py'))
    'a.b'
    >>> _dotpath_of_py_path(os.path.join('a', 'b.py'), 'pkg')
    'pkg.a.b'

    Both separators are understood, so the store's path convention doesn't matter:

    >>> _dotpath_of_py_path('a/b.py')
    'a.b'

    """
    if FOREIGN_PATH_SEP:
        py_path = py_path.replace(FOREIGN_PATH_SEP, os.path.sep)
    return py_path_to_dot_path(py_path, root_module_str).lstrip(".")


class ModuleImports(KvReader):
    """``Mapping`` from module dotpath to the tuple of imports of that module.

    :param src: Anything :class:`~tec.stores.PyFilesReader` accepts: a folder path,
        a module or package object, or the path of an ``__init__.py`` file.
    :param root_module_str: Prefix to give the module dotpaths (the keys).

    Note: the dotpath-to-file index is computed once, lazily, on first use -- files
    added to the folder afterwards will not show up in an existing instance.

    >>> import tempfile
    >>> from pathlib import Path
    >>> with tempfile.TemporaryDirectory() as root:
    ...     _ = Path(root, '__init__.py').write_text('')
    ...     _ = Path(root, 'a.py').write_text('import os\\nfrom json import dumps\\n')
    ...     s = ModuleImports(root, root_module_str='pkg')
    ...     keys, n = sorted(s), len(s)
    ...     names = [imp.name for imp in s['pkg.a']]
    >>> keys
    ['pkg.__init__', 'pkg.a']
    >>> n
    2
    >>> names
    ['os', 'json.dumps']

    """

    def __init__(self, src: Any, *, root_module_str: str = ""):
        self.store = PyFilesReader(src)
        self.root_module_str = root_module_str

    @cached_property
    def _path_of_dotpath(self) -> dict:
        """``{module_dotpath: store_key}`` index of the files of :attr:`store`."""
        return {
            _dotpath_of_py_path(path, self.root_module_str): path for path in self.store
        }

    def __iter__(self) -> Iterator[str]:
        return iter(self._path_of_dotpath)

    def __len__(self) -> int:
        return len(self._path_of_dotpath)

    def __contains__(self, k) -> bool:
        return k in self._path_of_dotpath

    def __getitem__(self, k) -> tuple:
        path = self._path_of_dotpath.get(k)
        if path is None:
            raise KeyError(
                f"No module found for dotpath {k!r} under {self.store.rootdir!r}. "
                f"Note that the dotpaths are prefixed with root_module_str="
                f"{self.root_module_str!r}."
            )
        return tuple(imports_in_code(self.store[path], filename=path))
