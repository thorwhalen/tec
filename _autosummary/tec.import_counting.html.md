# tec.import_counting

Counting dependencies.

#### NOTE
Several of the import_counting module’s functions require
having snakefood installed. See: [http://furius.ca/snakefood/doc/snakefood-doc.html#installation](http://furius.ca/snakefood/doc/snakefood-doc.html#installation)

### Functions

| [`base_module_name`](#tec.import_counting.base_module_name)(module_name_dot_path)         | Base name of dot path module name                                                            |
|-------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| [`imports_in_py_content`](#tec.import_counting.imports_in_py_content)(py_content)              | Generator of imported names parsed out (with regex) of input code (string)                   |
| `is_stdlib_module`(name)                                                                        |                                                                                              |
| [`mk_multiple_package_import_regex`](#tec.import_counting.mk_multiple_package_import_regex)(module_names) | Make a regular expression to parse out a specific modules names in the context of an import. |
| [`mk_single_package_import_regex`](#tec.import_counting.mk_single_package_import_regex)(module_name)    | Make a regular expression to parse out a specific module name in the context of an import.   |
| [`modules_imported`](#tec.import_counting.modules_imported)(obj[, only_base_name, ...])   | Generator of module names from obj.                                                          |
| [`modules_imported_by_module`](#tec.import_counting.modules_imported_by_module)(module)             | Generator of module names that are imported in a module.                                     |
| [`modules_imported_count`](#tec.import_counting.modules_imported_count)(obj[, ...])             | A dict containing the imported names and their counts, sorted from most frequent to least.   |
| [`modules_imported_under_folder`](#tec.import_counting.modules_imported_under_folder)(root)            | Generator of imported module (dot path) names                                                |

### tec.import_counting.base_module_name(module_name_dot_path)

Base name of dot path module name

```pycon
>>> base_module_name('os.path.join')
'os'
```

Note that relative import names will resolve to an empty string.

```pycon
>>> base_module_name("..relatively_imported")
''
```

### tec.import_counting.imports_in_py_content(py_content)

Generator of imported names parsed out (with regex) of input code (string)

```pycon
>>> list(imports_in_py_content("import inspect ,  sys ;  import os.path\n  from collections.abc import Mapping"))
['inspect', 'sys', 'os.path', 'collections.abc']
```

### tec.import_counting.mk_multiple_package_import_regex(module_names)

Make a regular expression to parse out a specific modules names in the context of an import.

### tec.import_counting.mk_single_package_import_regex(module_name)

Make a regular expression to parse out a specific module name in the context of an import.

### tec.import_counting.modules_imported(obj, only_base_name=False, exclude_stdlib=False)

Generator of module names from obj.

#### NOTE
The process uses regular expressions to parse out imported names from string contents.
The process in by no means accurate in all cases.
It may have false positives (strings that have import patterns, but are not actual code imports).
It may have false negatives (relative imports (as in `..name`) and “dynamically” imported, etc.

If you need something more precise, use `tec.imports` (which parses the code with
`ast` instead of matching patterns), or look into other tools (snakefood, for example).

* **Parameters:**
  * **obj** – module object, file or folder path, or anything that can resolve to that
  * **only_base_name** – If True, will only return the first part of the dot names
* **Returns:**
  Generator of module (dot path) names

```pycon
>>> import os.path  # single module
>>> list(modules_imported(os.path))
['os', 'sys', 'stat', 'genericpath', 'genericpath', 'pwd', 'pwd', 're', 're']
>>> import os  # package with several modules
>>> from collections import Counter
>>> Counter(modules_imported(os, only_base_name=True)).most_common()
[('nt', 5), ('posix', 4), ... ('warnings', 1), ('subprocess', 1)]
```

### tec.import_counting.modules_imported_by_module(module)

Generator of module names that are imported in a module.

* **Parameters:**
  **module** – The module specification, which could be a filepath, the actual code (string) of the module,
  or any python object (module or object therein – that can be resolved by inspect.getfile(module))
* **Returns:**
  A generator of strings showing the imported module names (dot paths)

The input can be a filepath

```pycon
>>> sorted(modules_imported_by_module(__file__))
['collections', 'importlib.util', 'io', 'os', 'os.path', 'pathlib', 're', 'sys', 'sysconfig', 'tec.stores', 'tec.util']
```

… a imported module object

```pycon
>>> import wave
>>> sorted(modules_imported_by_module(wave))
['audioop', 'builtins', 'chunk', 'collections', 'struct', 'sys']
```

… the string contents themselves

### tec.import_counting.modules_imported_count(obj, only_base_name=False, exclude_stdlib=False)

A dict containing the imported names and their counts, sorted from most frequent to least.

### tec.import_counting.modules_imported_under_folder(root)

Generator of imported module (dot path) names

* **Parameters:**
  **root**
* **Returns:**
