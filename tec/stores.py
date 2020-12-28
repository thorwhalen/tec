"""(py2store) stores (i.e. mapping interfaces) to access python files"""

import os
from py2store import wrap_kvs, filt_iter, KvReader
from py2store.filesys import mk_relative_path_store, DirCollection, FileStringReader


@filt_iter(filt=lambda k: k.endswith('.py') and '__pycache__' not in k)
@mk_relative_path_store(prefix_attr='rootdir')
class PkgFilesReader(FileStringReader, KvReader):
    """Mapping interface to .py files of a folder.
    Keys are relative .py paths.
    Values are the string contents of the .py file.
    """

    def init_file_contents(self):
        """Returns the string of contents of the __init__.py file if it exists, and None if not"""
        return self.get('__init__.py', None)

    def is_pkg(self):
        """Returns True if, and only if, the root is a pkg folder (i.e. has an __init__.py file)
        """
        return '__init__.py' in self


@filt_iter(filt=lambda k: not k.endswith('__pycache__'))
@wrap_kvs(key_of_id=lambda x: x[:-1],
          id_of_key=lambda x: x + os.path.sep)
@mk_relative_path_store(prefix_attr='rootdir')
class PkgReader(DirCollection, KvReader):
    def __getitem__(self, k):
        return PkgFilesReader(os.path.join(self.rootdir, k))
