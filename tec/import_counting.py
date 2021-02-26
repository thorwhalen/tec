"""
Counting dependencies.

Note: Several of the import_counting module's functions require
having snakefood installed. See: http://furius.ca/snakefood/doc/snakefood-doc.html#installation

"""
import re
import os
from io import StringIO
from collections import Counter
import inspect
from tec.util import resolve_module_contents
from tec.stores import PyFilesReader

file_sep = os.path.sep
module_import_regex_tmpl = "(?<=from) {package_name}|(?<=[^\s]import) {package_name}"

any_module_import_regex = re.compile(module_import_regex_tmpl.format(package_name=r'\w+'))

# r"(?<!from)import (?P<single>\w+)[^,]"
spaced_comma_re = re.compile(r"\s*,\s*")
# another_import_regex = re.compile(
#     r"from\s+(?P<from_import>[\w\.]+)\s+import"
#     r"|(?<!from)import (?P<multiple>[\w\.,]+)"
# )
another_import_regex = re.compile(
    r"^\s*from\s+(?P<from_import>[\w\.]+)\s+import"
    r"|^\s*import (?P<multiple>[\w\.,]+)"
)
commented_line_re = re.compile(r'\s*#')
token_re = re.compile(r'[\w\.]+')


def _normalize_line(line):
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


def mk_single_package_import_regex(module_name):
    return re.compile(module_import_regex_tmpl.format(package_name=module_name))


def mk_multiple_package_import_regex(module_names):
    if isinstance(module_names, str):
        module_names = [module_names]
    return re.compile('|'.join([mk_single_package_import_regex(x).pattern for x in module_names]))


def modules_imported_by_module(module):
    r"""
    Generator of module names that are imported in a module.

    :param module: The module specification, which could be a filepath, the actual code (string) of the module,
        or any python object (module or object therein -- that can be resolved by inspect.getfile(module))
    :return: A generator of strings showing the imported module names (dot paths)

    The input can be a filepath

    >>> list(modules_imported_by_module(__file__))
    ['re', 'os', 'io', 'collections', 'inspect', 'tec.util', 'tec.stores', 'os.path']

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


def base_modules_used_in_module(module):
    """
    Get a list of strings showing what base modules that are imported in a module.
    :param module: An actual module object the file of the module (as given by inspect.getfile(module)
    :return: A list of strings showing the imported base modules (i.e. the X of import X.Y.Z or from X.Y import Z).

    Note: Requires having snakefood installed:
    http://furius.ca/snakefood/doc/snakefood-doc.html#installation

    >>> sorted(base_modules_used_in_module(__file__))
    ['collections', 'inspect', 'io', 'os', 're', 'tec']

    """
    return set([re.compile('\w+').findall(x)[0] for x in modules_imported_by_module(module)])


# def base_module_imports_in_module_recursive(module):
#     """
#     Get a list of strings showing what base modules that are imported in a module, recursively.
#     It's the recursive version of the base_modules_used_in_module function.
#     Recursive in the sense that if module is a package module (i.e. containing a __init__.py and further submodules),
#     the base_modules_used_in_module function will be applied to all .py files under the mother folder.
#     Function returns a count (Counter object) of the number of modules where each base module was found.
#     :param module: An actual module object the file of the module (as given by inspect.getfile(module)
#     :param module_names: Modules to filter for.
#         None: Will grab all modules
#         A list or tuple: Of modules to grab
#         If not will assume module_names is a regex to apply to find module names
#     :return:
#     """
#     # if module_names is None:
#     #     module_names = any_module_import_regex
#     # elif isinstance(module_names, (tuple, list)):
#     #     module_names = mk_multiple_package_import_regex(module_names)
#
#     if inspect.ismodule(module):
#         module = inspect.getsourcefile(module)
#     if module.endswith('__init__.py'):
#         module = os.path.dirname(module)
#
#     if os.path.isdir(module):
#         c = Counter()
#         it = PyFilesReader(module).values()
#         # next(it)  # to skip the seed module itself, and not get into an infinite loop
#         for _module in it:
#             try:
#                 c.update(base_module_imports_in_module_recursive(_module))
#             except Exception as e:
#                 print('asdf')
#                 # if 'sfood-imports' in e.args[1]:
#                 #     raise RuntimeError("You don't have sfood-imports installed (snakefood), so I can't do my job")
#                 # else:
#                 #     print(("Error with module {}: {}".format(_module, e)))
#         return c
#     elif not os.path.isfile(module):
#         raise ValueError("module file not found: {}".format(module))
#
#     return Counter(base_modules_used_in_module(module))
