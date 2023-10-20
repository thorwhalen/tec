"""(dol) stores (i.e. mapping interfaces) to access python files"""
import re
from xdol.pystores import PyFilesReader, builtins_py_files, sitepackages_py_files

commented_header_re = re.compile("(\"\"\"|''')\s?.+")
triple_quotes_re = re.compile("\"\"\"|'''")
triple_quotes_ending_re = re.compile("\"\"\"$|'''$")


def _clean_str(string):
    return triple_quotes_re.sub("", string.strip())


def file_contents_to_short_description(file_contents: str, dflt=None, max_lines=4):
    lines = file_contents.split("\n")
    quotes_line_idx = next(
        (i for i, line in enumerate(lines[:max_lines]) if triple_quotes_re.match(line)),
        None,
    )
    if quotes_line_idx is not None:
        i = quotes_line_idx
        first_line_of_description = lines[i][3:].strip()
        if first_line_of_description:
            return _clean_str(first_line_of_description)
        i = min(len(lines), quotes_line_idx + 1)
        first_line_of_description = lines[i].strip()
        if first_line_of_description:
            return _clean_str(first_line_of_description)
    return dflt
    # m = commented_header_re.match(file_contents)
    # if m:
    #     t = m.group(0)[3:].strip()
    #     t = triple_quotes_ending_re.sub('', t)
    #     return t
    # else:
    #     return dflt


def find_short_description_for_pkg(s):
    """Generator of (pkg_name, short_description) pairs (using the header comments of init files as description)"""
    for k, v in s.items():
        if k.endswith("__init__.py") and (v.startswith('"""') or v.startswith("'''")):
            k = k[: -(len("__init__.py") + 1)]
            yield k, file_contents_to_short_description(v)


def py_files_with_contents_matching_pattern(files_src, pattern):
    """Yields (relative) file paths of .py files whose contents match pattern.

    :param files_src: Source of files. Module, package, folder, or __init__.py file.
    :param pattern: regular expression (string or re.Pattern object)

    Let's see what modules of asyncio contain the "import io" string:

    >>> import asyncio
    >>> set(py_files_with_contents_matching_pattern(asyncio, 'import io')).issuperset(
    ...     {'proactor_events.py', 'unix_events.py'})

    """

    pattern = re.compile(pattern)
    s = PyFilesReader(files_src)
    for k, v in s.items():
        if pattern.search(v):
            yield k
