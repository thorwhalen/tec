"""Tests for :mod:`tec.imports` and the deprecated :mod:`tec.findimports` shim."""

import importlib
import os
import warnings

import pytest

from tec.imports import (
    ABSOLUTE_IMPORT_LEVEL,
    CODE_STRING_FILENAME,
    ImportInfo,
    ModuleImports,
    base_package_of,
    count_imports,
    find_imports,
    ignore_parse_error,
    imports_in_code,
    imports_under_folder,
    raise_parse_error,
)

CODE = """
import os, sys
import os.path as osp
from collections.abc import Mapping, Sequence
from . import sibling
from ..pkg import thing

not_an_import = "import antigravity"  # import antigravity


def lazy():
    import json
    from tec import imports as _imports
"""


def _write(folder, name, contents):
    """Write ``contents`` to ``folder/name`` (creating parent folders) and return the path."""
    path = os.path.join(folder, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(contents)
    return path


# --------------------------------------------------------------------- imports_in_code


def test_imports_in_code_finds_every_flavor_of_import():
    names = [imp.name for imp in imports_in_code(CODE)]
    assert names == [
        "os",
        "sys",
        "os.path",
        "collections.abc.Mapping",
        "collections.abc.Sequence",
        "sibling",
        "pkg.thing",
        "json",
        "tec.imports",
    ]


def test_imports_in_code_is_not_fooled_by_import_looking_text():
    assert list(imports_in_code('x = "import antigravity"  # import antigravity')) == []
    assert list(imports_in_code("# import os\n'''from a import b'''\n")) == []


def test_imports_in_code_records_filename_lineno_and_level():
    (imp,) = imports_in_code("\n\nimport os\n", filename="a.py")
    assert imp == ImportInfo("os", "a.py", 3, ABSOLUTE_IMPORT_LEVEL)
    assert not imp.is_relative

    (relative,) = imports_in_code("from ..pkg import thing")
    assert relative.name == "pkg.thing"
    assert relative.level == 2
    assert relative.is_relative
    assert relative.filename == CODE_STRING_FILENAME


def test_imports_in_code_raises_on_unparsable_code():
    with pytest.raises(SyntaxError):
        list(imports_in_code("import ;", filename="broken.py"))


def test_import_info_is_hashable():
    assert len({ImportInfo("os"), ImportInfo("os")}) == 1


def test_base_package_of():
    assert base_package_of("collections.abc") == "collections"
    assert base_package_of(ImportInfo("os.path")) == "os"
    assert base_package_of(ImportInfo("sibling", level=1)) == ""


# ------------------------------------------------------------------------ find_imports


def test_find_imports_reads_the_file_and_records_its_path(tmp_path):
    path = _write(str(tmp_path), "a.py", "import os\nfrom json import dumps\n")
    imports = list(find_imports(path))
    assert [imp.name for imp in imports] == ["os", "json.dumps"]
    assert {imp.filename for imp in imports} == {path}


# ----------------------------------------------------------------- imports_under_folder


def test_imports_under_folder_walks_nested_py_files(tmp_path):
    root = str(tmp_path)
    _write(root, "a.py", "import os\n")
    _write(root, os.path.join("sub", "b.py"), "import json\n")
    _write(root, "not_python.txt", "import nope\n")
    assert sorted(imp.name for imp in imports_under_folder(root)) == ["json", "os"]


def test_imports_under_folder_honors_path_filt(tmp_path):
    root = str(tmp_path)
    _write(root, "a.py", "import os\n")
    _write(root, "a_test.py", "import json\n")
    kept = imports_under_folder(root, path_filt=lambda p: not p.endswith("_test.py"))
    assert [imp.name for imp in kept] == ["os"]


def test_imports_under_folder_warns_and_skips_unparsable_files_by_default(tmp_path):
    root = str(tmp_path)
    _write(root, "good.py", "import os\n")
    _write(root, "bad.py", "this is (not python\n")
    with pytest.warns(UserWarning, match="couldn't parse it"):
        names = [imp.name for imp in imports_under_folder(root)]
    assert names == ["os"]


def test_imports_under_folder_on_parse_error_strategies_are_injectable(tmp_path):
    root = str(tmp_path)
    _write(root, "good.py", "import os\n")
    _write(root, "bad.py", "this is (not python\n")

    with warnings.catch_warnings():
        warnings.simplefilter("error")  # any warning would fail the test
        names = [
            imp.name
            for imp in imports_under_folder(root, on_parse_error=ignore_parse_error)
        ]
    assert names == ["os"]

    with pytest.raises(SyntaxError):
        list(imports_under_folder(root, on_parse_error=raise_parse_error))

    seen = []
    list(imports_under_folder(root, on_parse_error=lambda e, p: seen.append(p)))
    assert seen == ["bad.py"]


# ---------------------------------------------------------------------- count_imports


def test_count_imports_counts_base_packages_by_default(tmp_path):
    root = str(tmp_path)
    _write(root, "a.py", "import os\nfrom os import path\n")
    _write(root, "b.py", "import os.path\nimport json\n")
    assert dict(count_imports(root)) == {"os": 3, "json": 1}


def test_count_imports_import_key_is_injectable(tmp_path):
    root = str(tmp_path)
    _write(root, "a.py", "import os.path\nimport os.path\n")
    counts = count_imports(root, import_key=lambda imp: imp.name)
    assert dict(counts) == {"os.path": 2}


# ---------------------------------------------------------------------- ModuleImports


def test_module_imports_maps_dotpaths_to_imports(tmp_path):
    root = str(tmp_path)
    _write(root, "__init__.py", "")
    _write(root, "a.py", "import os\nfrom json import dumps\n")
    _write(root, os.path.join("sub", "b.py"), "import re\n")

    s = ModuleImports(root, root_module_str="pkg")
    assert sorted(s) == ["pkg.__init__", "pkg.a", "pkg.sub.b"]
    assert len(s) == 3
    assert "pkg.a" in s
    assert "pkg.nope" not in s
    assert [imp.name for imp in s["pkg.a"]] == ["os", "json.dumps"]
    assert [imp.name for imp in s["pkg.sub.b"]] == ["re"]


def test_module_imports_without_a_root_module_str_has_no_leading_dot(tmp_path):
    root = str(tmp_path)
    _write(root, "__init__.py", "")
    _write(root, "a.py", "import os\n")
    s = ModuleImports(root)
    assert sorted(s) == ["__init__", "a"]
    assert [imp.name for imp in s["a"]] == ["os"]


def test_module_imports_missing_key_error_is_informative(tmp_path):
    root = str(tmp_path)
    _write(root, "__init__.py", "")
    s = ModuleImports(root, root_module_str="pkg")
    with pytest.raises(KeyError) as excinfo:
        s["nope"]
    message = str(excinfo.value)
    # says what was asked for, where it looked, and the likely cause (the prefix)
    assert "nope" in message
    assert "root_module_str" in message and "pkg" in message


def test_dotpath_of_py_path_accepts_either_path_separator():
    """The store's path convention (native or '/') must not change the keys."""
    from tec.imports import _dotpath_of_py_path

    assert _dotpath_of_py_path(os.path.join("a", "b.py")) == "a.b"
    assert _dotpath_of_py_path("a/b.py") == "a.b"
    assert _dotpath_of_py_path("a/b.py", "pkg") == "pkg.a.b"


def test_module_imports_can_read_a_real_package():
    """The store accepts a module object, not just a folder path."""
    import tec

    s = ModuleImports(tec, root_module_str="tec")
    assert "tec.imports" in s
    assert "ast" in {imp.name for imp in s["tec.imports"]}


# ---------------------------------------------------- deprecated tec.findimports shim


def test_findimports_shim_still_importable_as_a_submodule():
    """``ut`` (and any other downstream) does ``from tec import findimports``."""
    from tec import findimports

    assert findimports.find_imports is find_imports


def test_findimports_shim_warns_on_import():
    import tec.findimports

    with pytest.warns(DeprecationWarning, match="tec.imports"):
        importlib.reload(tec.findimports)


@pytest.mark.parametrize(
    "name", ["ModuleGraph", "ImportFinder", "ModulesColl", "main", "file_sep"]
)
def test_findimports_shim_gives_an_informative_error_for_removed_names(name):
    import tec.findimports as fi

    with pytest.raises(AttributeError) as excinfo:
        getattr(fi, name)
    message = str(excinfo.value)
    assert name in message
    assert "GPL" in message and "Apache-2.0" in message


def test_findimports_shim_gives_a_normal_error_for_names_that_never_existed():
    import tec.findimports as fi

    with pytest.raises(AttributeError, match="no attribute 'never_was_a_thing'"):
        fi.never_was_a_thing


def test_findimports_shim_forwards_to_the_new_implementation(tmp_path):
    import tec.findimports as fi

    root = str(tmp_path)
    _write(root, "a.py", "import os.path\nimport json\n")
    assert sorted(imp.name for imp in fi.re_find_imports(root)) == ["json", "os.path"]
    assert dict(fi.count_imports(root)) == {"os": 1, "json": 1}


def test_tec_exposes_the_import_finding_api_at_the_top_level():
    import tec

    assert tec.find_imports is find_imports
    assert tec.count_imports is count_imports
    assert tec.ImportInfo is ImportInfo
    assert tec.ModuleImports is ModuleImports
