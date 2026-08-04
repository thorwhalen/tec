"""Guard against foreign (licence-incompatible) source being vendored into ``tec``.

``tec`` is distributed under Apache-2.0. It once shipped a vendored copy of a
GPL-2.0-or-later project, which quietly made every ``tec`` release -- and every
package depending on it -- carry incompatible terms.

The test here is deliberately blunt: no file of the package may contain a foreign
licence grant or a copyright notice. If a future change legitimately needs one,
that is a decision to be made explicitly (by editing the package's declared
licence), not by silently pasting a file in.

"""

import re
from pathlib import Path

import tec

#: Root of the installed/importable ``tec`` package.
PKG_ROOT = Path(tec.__file__).parent

#: This test module -- excluded from the scan, since it necessarily spells out the
#: very markers it is looking for.
THIS_FILE = Path(__file__).resolve()

#: Directory names never scanned (build/cache artifacts, not source).
EXCLUDED_DIR_NAMES = frozenset({"__pycache__", ".ipynb_checkpoints"})

#: Substrings whose presence in a source file signals a foreign licence grant.
FOREIGN_LICENSE_MARKERS = (
    "GNU General Public License",
    "GNU Lesser General Public License",
    "Mozilla Public License",
    "This program is free software",
    "redistribute it and/or modify",
    "__licence__",
    "__license__",
)

#: A copyright notice line. Third party code almost always carries one; ``tec``'s
#: own modules carry none (the package's LICENSE file is the single place for it).
COPYRIGHT_RE = re.compile(r"^\s*(?:#\s*)?Copyright\b", re.IGNORECASE | re.MULTILINE)


def py_files_of_package():
    """Generate the ``.py`` files of the ``tec`` package that should be scanned."""
    for path in sorted(PKG_ROOT.rglob("*.py")):
        if EXCLUDED_DIR_NAMES.isdisjoint(path.parts) and path.resolve() != THIS_FILE:
            yield path


def test_there_are_files_to_scan():
    """Sanity check: a scan that finds nothing to scan would vacuously pass."""
    assert len(list(py_files_of_package())) > 5


def test_no_foreign_license_grant_in_package_source():
    """No module of the package embeds a foreign licence grant."""
    offenders = {}
    for path in py_files_of_package():
        contents = path.read_text(encoding="utf-8", errors="replace")
        found = [marker for marker in FOREIGN_LICENSE_MARKERS if marker in contents]
        if found:
            offenders[path.relative_to(PKG_ROOT).as_posix()] = found
    assert not offenders, (
        f"Foreign licence text found in tec source, but tec is Apache-2.0: {offenders}"
    )


def test_no_foreign_copyright_notice_in_package_source():
    """No module of the package carries a copyright notice of its own."""
    offenders = [
        path.relative_to(PKG_ROOT).as_posix()
        for path in py_files_of_package()
        if COPYRIGHT_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    ]
    assert not offenders, (
        f"Copyright notice(s) found in tec source, but tec is Apache-2.0 and its "
        f"only copyright statement belongs in LICENSE: {offenders}"
    )
