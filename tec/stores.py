"""(py2store) stores (i.e. mapping interfaces) to access python files"""
import site
import os
import re
from py2store import wrap_kvs, filt_iter, KvReader, cached_keys
from py2store.filesys import mk_relative_path_store, DirCollection, FileBytesReader
from tec.util import decode_or_default


@filt_iter(filt=lambda k: k.endswith('.py') and '__pycache__' not in k)
@mk_relative_path_store(prefix_attr='rootdir')
class PyFilesBytes(FileBytesReader):
    """Mapping interface to .py files' bytes"""


@wrap_kvs(obj_of_data=decode_or_default)
@filt_iter(filt=lambda k: k.endswith('.py') and '__pycache__' not in k)
@mk_relative_path_store(prefix_attr='rootdir')
class PyFilesReader(FileBytesReader, KvReader):
    """Mapping interface to .py files of a folder.
    Keys are relative .py paths.
    Values are the string contents of the .py file.

    Important Note: If the byte contents of the .py file can't be decoded (with a simple bytes.decode()),
    an empty string will be returned as it's value (i.e. contents).

    """

    def init_file_contents(self):
        """Returns the string of contents of the __init__.py file if it exists, and None if not"""
        return self.get('__init__.py', None)

    def is_pkg(self):
        """Returns True if, and only if, the root is a pkg folder (i.e. has an __init__.py file)
        """
        return '__init__.py' in self


PkgFilesReader = PyFilesReader  # back-compatibility alias

builtins_rootdir = os.path.dirname(os.__file__)
builtins_py_files = cached_keys(PyFilesReader(builtins_rootdir))

sitepackages_rootdir = next(iter(site.getsitepackages()))
sitepackages_py_files = cached_keys(PyFilesReader(sitepackages_rootdir))


@filt_iter(filt=lambda k: not k.endswith('__pycache__'))
@wrap_kvs(key_of_id=lambda x: x[:-1],
          id_of_key=lambda x: x + os.path.sep)
@mk_relative_path_store(prefix_attr='rootdir')
class PkgReader(DirCollection, KvReader):
    def __getitem__(self, k):
        return PyFilesReader(os.path.join(self.rootdir, k))


commented_header_re = re.compile('("""|\'\'\')\s?.+')
triple_quotes_re = re.compile('"""|\'\'\'')
triple_quotes_ending_re = re.compile('"""$|\'\'\'$')


def _clean_str(string):
    return triple_quotes_re.sub('', string.strip())


def file_contents_to_short_description(file_contents: str, dflt=None, max_lines=4):
    lines = file_contents.split('\n')
    quotes_line_idx = next(
        (i for i, line in enumerate(lines[:max_lines])
         if triple_quotes_re.match(line)),
        None)
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
        if k.endswith('__init__.py') and (v.startswith('"""') or v.startswith("'''")):
            k = k[:-(len('__init__.py') + 1)]
            yield k, file_contents_to_short_description(v)
