"""
Counting dependencies.

Note: Several of the import_counting module's functions require
having snakefood installed. See: http://furius.ca/snakefood/doc/snakefood-doc.html#installation

"""
import re
import os
from io import StringIO
from collections import Counter
from tec.util import resolve_module_contents, resolve_to_folder, resolve_module_filepath
from tec.stores import PyFilesReader

file_sep = os.path.sep
module_import_regex_tmpl = "(?<=from) {package_name}|(?<=[^\s]import) {package_name}"

any_module_import_regex = re.compile(module_import_regex_tmpl.format(package_name=r'\w+'))

spaced_comma_re = re.compile(r"\s*,\s*")
another_import_regex = re.compile(
    r"^\s*from\s+(?P<from_import>[\w\.]+)\s+import"
    r"|^\s*import (?P<multiple>[\w\.,]+)"
)
commented_line_re = re.compile(r'\s*#')
token_re = re.compile(r'[\w\.]+')


def mk_single_package_import_regex(module_name):
    """Make a regular expression to parse out a specific module name in the context of an import."""
    return re.compile(module_import_regex_tmpl.format(package_name=module_name))


def mk_multiple_package_import_regex(module_names):
    """Make a regular expression to parse out a specific modules names in the context of an import."""
    if isinstance(module_names, str):
        module_names = [module_names]
    return re.compile('|'.join([mk_single_package_import_regex(x).pattern for x in module_names]))


def modules_imported(obj, only_base_name=False):
    """Generator of module names from obj.
    
    Note: The process uses regular expressions to parse out imported names from string contents.
    The process in by no means accurate in all cases. 
    It may have false positives (strings that have import patterns, but are not actual code imports).
    It may have false negatives (relative imports (as in ``..name``) and "dynamically" imported, etc.

    If you need something more precise, look into other tools (snakefood or findimports for example).
    
    :param obj: module object, file or folder path, or anything that can resolve to that
    :param only_base_name: If True, will only return the first part of the dot names
    :return: Generator of module (dot path) names
    
    
    >>> import os.path  # single module
    >>> list(modules_imported(os.path))  # list of names in the order they were found
    ['os', 'sys', 'stat', 'genericpath', 'genericpath', 'pwd', 'pwd', 're', 're']
    >>> import os  # package with several modules
    >>> from collections import Counter
    >>> Counter(modules_imported(os, only_base_name=True)).most_common()  #doctest: +ELLIPSIS
    [('nt', 5), ('posix', 4), ... ('warnings', 1), ('subprocess', 1)]

    """
    if only_base_name:
        yield from map(base_module_name, modules_imported(obj))
    else:
        obj = resolve_module_filepath(obj, assert_output_is_existing_filepath=False)
        if obj.endswith('__init__.py'):
            folder = resolve_to_folder(obj)
            yield from modules_imported_under_folder(folder)
        else:  # so obj is a filepath or the code string to be analyzed
            yield from modules_imported_by_module(obj)


def modules_imported_count(obj, only_base_name=False):
    """A dict containing the imported names and their counts, sorted from most frequent to least.
    """
    return dict(Counter(set(modules_imported(obj, only_base_name=only_base_name))))


def _normalize_line(line):
    """Compress any comma separated items so that no space appears before or after the commas
    >>> _normalize_line("here, is  ,   a stronge ,csv   line")
    'here,is,a stronge,csv   line'
    """
    return spaced_comma_re.sub(',', line)


def imports_in_py_content(py_content: str):
    r"""Generator of imported names parsed out (with regex) of input code (string)

    >>> list(imports_in_py_content("import inspect ,  sys ;  import os.path\n  from collections.abc import Mapping"))
    ['inspect', 'sys', 'os.path', 'collections.abc']

    """

    for line in StringIO(py_content + '\n'):
        if not commented_line_re.match(line):
            for subline in _normalize_line(line).split(';'):
                r = another_import_regex.search(subline)
                if r is not None:
                    import_str = next((v for k, v in r.groupdict().items() if v is not None), None)
                    if import_str is not None:
                        for import_name in import_str.split(','):
                            yield import_name


def modules_imported_by_module(module):
    r"""
    Generator of module names that are imported in a module.

    :param module: The module specification, which could be a filepath, the actual code (string) of the module,
        or any python object (module or object therein -- that can be resolved by inspect.getfile(module))
    :return: A generator of strings showing the imported module names (dot paths)

    The input can be a filepath

    >>> list(modules_imported_by_module(__file__))
    ['re', 'os', 'io', 'collections', 'tec.util', 'tec.stores', 'os.path']

    ... a imported module object

    >>> import wave
    >>> list(modules_imported_by_module(wave))
    ['builtins', 'audioop', 'struct', 'sys', 'chunk', 'collections', 'warnings']

    ... the string contents themselves

    """
    module_contents = resolve_module_contents(module)
    yield from imports_in_py_content(module_contents)

    #
    # t = subprocess.check_output(['sfood-imports', '-u', module])
    # return [x for x in t.split('\n') if len(x) > 0]


def modules_imported_under_folder(root):
    """Generator of imported module (dot path) names

    :param root:
    :return:
    """
    root = resolve_to_folder(root)
    for filename, contents in PyFilesReader(root).items():
        yield from modules_imported_by_module(contents)


base_name_re = re.compile('\w+')


def base_module_name(module_name_dot_path):
    """Base name of dot path module name
    >>> base_module_name('os.path.join')
    'os'

    Note that relative import names will resolve to an empty string.

    >>> base_module_name("..relatively_imported")
    ''

    """
    r = base_name_re.match(module_name_dot_path)
    if r:
        return r.group(0)
    else:
        return ""
