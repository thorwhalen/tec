"""Deprecated compatibility layer -- use :mod:`tec.imports` instead.

``tec`` used to ship, under this module name, a vendored (lightly edited) copy of
the third party ``findimports`` project. That copy was distributed under the
GPL-2.0-or-later, which is incompatible with ``tec``'s own Apache-2.0 terms, so it
has been removed.

What replaces it:

- Import finding is now done by :mod:`tec.imports`, an independent implementation
  written against the standard library's ``ast``. The functions of this module
  simply forward to it.
- The names that had no ``tec`` equivalent -- essentially the module *graph*
  machinery (``ModuleGraph``, ``ImportFinder``, ``Module``, ...) -- are gone. If
  you need them, install the upstream project yourself
  (``pip install findimports``), keeping in mind that doing so subjects your work
  to *its* licence rather than ``tec``'s.

Importing this module emits a ``DeprecationWarning``. Asking it for one of the
removed names raises an ``AttributeError`` that says what to do instead:

>>> import tec.findimports as fi
>>> fi.ModuleGraph  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
  ...
AttributeError: ...

"""

from typing import Any, Callable
from warnings import warn

# Deliberate re-exports: downstream code did ``from tec.findimports import <name>``.
from tec.imports import (  # noqa: F401
    ImportInfo,
    ModuleImports,
    base_package_of,
    find_imports,
    imports_in_code,
    imports_under_folder,
)
from tec.imports import count_imports as _count_imports

#: Module that supersedes this one.
REPLACEMENT_MODULE = "tec.imports"

#: Advice for the names that only the (GPL) upstream project provides.
UPSTREAM_ONLY_ADVICE = (
    "there is no tec equivalent; install the upstream (GPL-2.0-or-later) project "
    "with `pip install findimports` if you need it"
)

#: Names the removed vendored implementation used to provide, mapped to what to do
#: instead. Kept as data (rather than in the error-raising code) so that the
#: "what happened to X?" answers are a single, extensible source of truth.
REMOVED_NAMES = {
    "ModuleGraph": UPSTREAM_ONLY_ADVICE,
    "ImportFinder": f"use {REPLACEMENT_MODULE}.imports_in_code",
    "ImportFinderAndNameTracker": f"use {REPLACEMENT_MODULE}.imports_in_code",
    "find_imports_and_track_names": f"use {REPLACEMENT_MODULE}.find_imports",
    "adjust_lineno": "there is no tec equivalent; ast node line numbers are used as is",
    "Module": UPSTREAM_ONLY_ADVICE,
    "ModuleCycle": UPSTREAM_ONLY_ADVICE,
    "Scope": "there is no tec equivalent",
    "main": "there is no tec equivalent; this module has no command line interface",
    "quote": "there is no tec equivalent; it was a graphviz-output helper",
    "ModulesColl": f"use {REPLACEMENT_MODULE}.ModuleImports (or tec.modules.ModulesReader)",
    "ModuleImportsBase": f"use {REPLACEMENT_MODULE}.ModuleImports",
    "modobj_to_modname": f"use {REPLACEMENT_MODULE}.ModuleImports",
    "modname_to_modobj": f"use {REPLACEMENT_MODULE}.ModuleImports",
    "iter_relative_files_and_folder": "use tec.stores.PyFilesReader",
    "pattern_filter": "use tec.stores.PyFilesReader (or a plain re.compile(...).match)",
    "recursive_file_walk_iterator_with_filepath_filter": "use tec.stores.PyFilesReader",
    "file_sep": "use os.path.sep",
}

#: Template of the error raised when a removed name is requested.
REMOVED_NAME_ERROR_TEMPLATE = (
    "{module}.{name} was removed: it came from a vendored GPL-2.0-or-later copy of "
    "the third party `findimports` project, which was incompatible with tec's "
    "Apache-2.0 licence. Instead, {advice}."
)

#: Message of the ``DeprecationWarning`` emitted when this module is imported.
DEPRECATION_MESSAGE = (
    f"tec.findimports is deprecated: use {REPLACEMENT_MODULE} instead. "
    "The vendored GPL-2.0-or-later implementation this module used to hold was "
    "removed (licence incompatibility); what is left is a thin forwarding layer."
)


def _is_py_path(path: str) -> bool:
    """True if, and only if, ``path`` looks like a python file path."""
    return path.endswith(".py")


def re_find_imports(rootdir: Any, pathfilt: Callable[[str], bool] = _is_py_path):
    """Deprecated alias of :func:`tec.imports.imports_under_folder`.

    Note the (harmless for the default) semantic difference: ``pathfilt`` is now
    applied to store-relative paths, not to absolute ones.

    >>> import tempfile
    >>> from pathlib import Path
    >>> with tempfile.TemporaryDirectory() as root:
    ...     _ = Path(root, 'a.py').write_text('import os\\n')
    ...     names = [imp.name for imp in re_find_imports(root)]
    >>> names
    ['os']

    """
    return imports_under_folder(rootdir, path_filt=pathfilt)


def count_imports(
    rootdir: Any,
    pathfilt: Callable[[str], bool] = _is_py_path,
    import_obj_func: Callable[[ImportInfo], Any] = base_package_of,
):
    """Deprecated alias of :func:`tec.imports.count_imports`.

    >>> import tempfile
    >>> from pathlib import Path
    >>> with tempfile.TemporaryDirectory() as root:
    ...     _ = Path(root, 'a.py').write_text('import os.path\\nimport json\\n')
    ...     counts = count_imports(root)
    >>> sorted(counts.items())
    [('json', 1), ('os', 1)]

    """
    return _count_imports(rootdir, path_filt=pathfilt, import_key=import_obj_func)


def __getattr__(name: str):
    """Give an informative error for names the licence cleanup removed (PEP 562)."""
    advice = REMOVED_NAMES.get(name)
    if advice is not None:
        raise AttributeError(
            REMOVED_NAME_ERROR_TEMPLATE.format(
                module=__name__, name=name, advice=advice
            )
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
