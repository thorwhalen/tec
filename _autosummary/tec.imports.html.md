# tec.imports

Find the imports of python code, using the standard library’s `ast`.

This module answers the question  *“what does this code import?”* by parsing the
code into an abstract syntax tree and walking it – so, unlike the regex-based
[`tec.import_counting`](tec.import_counting.html.md#module-tec.import_counting), it is not fooled by import-looking strings, comments,
or line continuations.

The simple thing is simple:

```pycon
>>> [imp.name for imp in imports_in_code("import os\nfrom json import dumps")]
['os', 'json.dumps']
```

The interface has three levels, from most to least specific:

- [`imports_in_code()`](#tec.imports.imports_in_code): imports of a string of python code
- [`find_imports()`](#tec.imports.find_imports): imports of a single `.py` file
- [`imports_under_folder()`](#tec.imports.imports_under_folder) / [`count_imports()`](#tec.imports.count_imports): imports of every `.py`
  file under a folder – reached through the `PyFilesReader`
  store, so a “folder” can also be a module object, a package, or the path of an
  `__init__.py` file

[`ModuleImports`](#tec.imports.ModuleImports) offers the same information as a `Mapping` from module
dotpath to the imports of that module.

#### NOTE
this module replaces the vendored copy of the (GPL-2.0-or-later) third
party `findimports` project that `tec` used to ship as `tec.findimports`.
It is an independent implementation, written against the standard library, so
that `tec` can be distributed under its own Apache-2.0 terms.

### Module Attributes

| [`CODE_STRING_FILENAME`](#tec.imports.CODE_STRING_FILENAME)             | Placeholder used as the `filename` of imports parsed from a code string.                                                 |
|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| [`ABSOLUTE_IMPORT_LEVEL`](#tec.imports.ABSOLUTE_IMPORT_LEVEL)            | Value of [`ImportInfo.level`](#tec.imports.ImportInfo.level) for an absolute (non-relative) import.        |
| [`DFLT_IMPORT_KEY`](#tec.imports.DFLT_IMPORT_KEY)(imp)             | Default aggregation key of [`count_imports()`](#tec.imports.count_imports): the top-level package name. |
| [`DFLT_PATH_FILT`](#tec.imports.DFLT_PATH_FILT)                   | `None`, i.e. no filtering beyond the store's own restriction to `.py` files.                                             |
| [`DFLT_ON_PARSE_ERROR`](#tec.imports.DFLT_ON_PARSE_ERROR)(error, path) | Default reaction to a file that can't be parsed while walking a folder.                                                  |
| [`FOREIGN_PATH_SEP`](#tec.imports.FOREIGN_PATH_SEP)                 | Path separator that is legal but not native on this platform (`'/'` on Windows, `None` elsewhere).                       |

### Functions

| [`DFLT_IMPORT_KEY`](#tec.imports.DFLT_IMPORT_KEY)(imp)                            | Default aggregation key of [`count_imports()`](#tec.imports.count_imports): the top-level package name.   |
|--------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| [`DFLT_ON_PARSE_ERROR`](#tec.imports.DFLT_ON_PARSE_ERROR)(error, path)                | Default reaction to a file that can't be parsed while walking a folder.                                                    |
| [`base_package_of`](#tec.imports.base_package_of)(imp)                            | The top-level package name of an import (`''` for relative imports).                                                       |
| [`count_imports`](#tec.imports.count_imports)(src, \*[, path_filt, ...])        | Count the imports of every `.py` file under `src`.                                                                         |
| [`find_imports`](#tec.imports.find_imports)(filename)                          | Generate the [`ImportInfo`](#tec.imports.ImportInfo) of every import of the `.py` file `filename`.     |
| [`ignore_parse_error`](#tec.imports.ignore_parse_error)(error, path)                 | `on_parse_error` strategy: silently skip the file.                                                                         |
| [`imports_in_code`](#tec.imports.imports_in_code)(code, \*[, filename])           | Generate the [`ImportInfo`](#tec.imports.ImportInfo) of every import found in `code`.                  |
| [`imports_under_folder`](#tec.imports.imports_under_folder)(src, \*[, path_filt, ...]) | Generate the [`ImportInfo`](#tec.imports.ImportInfo) of every `.py` file under `src`.                  |
| [`raise_parse_error`](#tec.imports.raise_parse_error)(error, path)                  | `on_parse_error` strategy: let the `SyntaxError` propagate.                                                                |
| [`warn_of_parse_error`](#tec.imports.warn_of_parse_error)(error, path)                | `on_parse_error` strategy: warn about the file, then skip it.                                                              |

### Classes

| [`ImportInfo`](#tec.imports.ImportInfo)(name[, filename, lineno, level])   | A single imported name, along with where it was found.                |
|------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| [`ModuleImports`](#tec.imports.ModuleImports)(src, \*[, root_module_str])     | `Mapping` from module dotpath to the tuple of imports of that module. |

### tec.imports.ABSOLUTE_IMPORT_LEVEL *= 0*

Value of [`ImportInfo.level`](#tec.imports.ImportInfo.level) for an absolute (non-relative) import.

### tec.imports.CODE_STRING_FILENAME *= '<string>'*

Placeholder used as the `filename` of imports parsed from a code string.

### tec.imports.DFLT_IMPORT_KEY(imp)

Default aggregation key of [`count_imports()`](#tec.imports.count_imports): the top-level package name.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### tec.imports.DFLT_ON_PARSE_ERROR(error, path)

Default reaction to a file that can’t be parsed while walking a folder. Folders
of real-world code routinely contain a stray py2 (or templated) file, so the
default is to warn and move on instead of aborting the whole walk.

* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)

### tec.imports.DFLT_PATH_FILT *= None*

`None`, i.e. no filtering beyond the store’s own
restriction to `.py` files.

* **Type:**
  Default file-path predicate

### tec.imports.FOREIGN_PATH_SEP *= None*

Path separator that is legal but not native on this platform (`'/'` on Windows,
`None` elsewhere). File stores are not required to use the native one.

### *class* tec.imports.ImportInfo(name, filename='<string>', lineno=0, level=0)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A single imported name, along with where it was found.

```pycon
>>> imp = ImportInfo("os.path", "a.py", 3)
>>> imp.name, imp.lineno, imp.is_relative
('os.path', 3, False)
```

Relative imports carry the number of leading dots in `level`:

```pycon
>>> ImportInfo("sibling", "a.py", 1, level=1).is_relative
True
```

#### filename *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)* *= '<string>'*

File the import was found in ([`CODE_STRING_FILENAME`](#tec.imports.CODE_STRING_FILENAME) if unknown).

#### *property* is_relative *: [bool](https://docs.python.org/3/builtins/functions.html#bool)*

True if, and only if, this is a relative (`from .x import y`) import.

#### level *: [int](https://docs.python.org/3/builtins/functions.html#int)* *= 0*

Number of leading dots of a relative import (`0` if absolute).

#### lineno *: [int](https://docs.python.org/3/builtins/functions.html#int)* *= 0*

1-based line number of the `import`/`from` statement.

#### name *: [str](https://docs.python.org/3/builtins/stdtypes.html#str)*

Dotted name of what is imported (e.g. `'os.path'`, `'json.dumps'`).

### *class* tec.imports.ModuleImports(src, , root_module_str='')

Bases: `KvReader`

`Mapping` from module dotpath to the tuple of imports of that module.

* **Parameters:**
  * **src** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Anything `PyFilesReader` accepts: a folder path,
    a module or package object, or the path of an `__init__.py` file.
  * **root_module_str** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Prefix to give the module dotpaths (the keys).

#### NOTE
the dotpath-to-file index is computed once, lazily, on first use – files
added to the folder afterwards will not show up in an existing instance.

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> with tempfile.TemporaryDirectory() as root:
...     _ = Path(root, '__init__.py').write_text('')
...     _ = Path(root, 'a.py').write_text('import os\nfrom json import dumps\n')
...     s = ModuleImports(root, root_module_str='pkg')
...     keys, n = sorted(s), len(s)
...     names = [imp.name for imp in s['pkg.a']]
>>> keys
['pkg.__init__', 'pkg.a']
>>> n
2
>>> names
['os', 'json.dumps']
```

### tec.imports.base_package_of(imp)

The top-level package name of an import (`''` for relative imports).

```pycon
>>> base_package_of("collections.abc")
'collections'
>>> base_package_of(ImportInfo("os.path"))
'os'
```

A relative import has no resolvable top-level package, so it maps to `''`:

```pycon
>>> base_package_of(ImportInfo("sibling", level=1))
''
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### tec.imports.count_imports(src, \*, path_filt=None, import_key=<function base_package_of>, on_parse_error=<function warn_of_parse_error>)

Count the imports of every `.py` file under `src`.

* **Parameters:**
  * **src** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Anything `PyFilesReader` accepts (see
    [`imports_under_folder()`](#tec.imports.imports_under_folder)).
  * **path_filt** ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`bool`](https://docs.python.org/3/builtins/functions.html#bool)]]) – Optional predicate on the store’s (relative) file paths.
  * **import_key** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`ImportInfo`](#tec.imports.ImportInfo)], [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – What to count: applied to each [`ImportInfo`](#tec.imports.ImportInfo), it
    returns the value that is tallied. Defaults to [`base_package_of()`](#tec.imports.base_package_of),
    i.e. the top-level package name.
  * **on_parse_error** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`SyntaxError`](https://docs.python.org/3/builtins/exceptions.html#SyntaxError), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`None`](https://docs.python.org/3/builtins/constants.html#None)]) – See [`imports_under_folder()`](#tec.imports.imports_under_folder).
* **Return type:**
  [`Counter`](https://docs.python.org/3/library/collections.html#collections.Counter)
* **Returns:**
  A [`collections.Counter`](https://docs.python.org/3/library/collections.html#collections.Counter).

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> with tempfile.TemporaryDirectory() as root:
...     _ = Path(root, 'a.py').write_text('import os\nfrom os import path\n')
...     _ = Path(root, 'b.py').write_text('import os.path\nimport json\n')
...     counts = count_imports(root)
...     full = count_imports(root, import_key=lambda imp: imp.name)
>>> sorted(counts.items())
[('json', 1), ('os', 3)]
>>> sorted(full.items())
[('json', 1), ('os', 1), ('os.path', 2)]
```

### tec.imports.find_imports(filename)

Generate the [`ImportInfo`](#tec.imports.ImportInfo) of every import of the `.py` file `filename`.

* **Parameters:**
  **filename** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Path of the python file to parse.
* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`ImportInfo`](#tec.imports.ImportInfo)]
* **Returns:**
  A generator of [`ImportInfo`](#tec.imports.ImportInfo).

```pycon
>>> imports = list(find_imports(__file__))
>>> "ast" in {imp.name for imp in imports}
True
>>> {imp.filename for imp in imports} == {__file__}
True
```

### tec.imports.ignore_parse_error(error, path)

`on_parse_error` strategy: silently skip the file.

* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)

### tec.imports.imports_in_code(code, , filename='<string>')

Generate the [`ImportInfo`](#tec.imports.ImportInfo) of every import found in `code`.

* **Parameters:**
  * **code** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The python source to parse.
  * **filename** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – What to record as the origin of the imports found.
* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`ImportInfo`](#tec.imports.ImportInfo)]
* **Returns:**
  A generator of [`ImportInfo`](#tec.imports.ImportInfo).

```pycon
>>> code = '''
... import os, sys
... import os.path as osp
... from collections.abc import Mapping
... from . import sibling
... from ..pkg import thing
... '''
>>> [imp.name for imp in imports_in_code(code)]
['os', 'sys', 'os.path', 'collections.abc.Mapping', 'sibling', 'pkg.thing']
```

Unlike a regex-based scan, text that merely *looks* like an import is ignored:

```pycon
>>> list(imports_in_code('x = "import antigravity"  # import antigravity'))
[]
```

Imports nested in functions, classes, `try` blocks etc. are included:

```pycon
>>> [imp.name for imp in imports_in_code("def f():\n    import lazily\n")]
['lazily']
```

Code that doesn’t parse raises a `SyntaxError` naming the offending file:

```pycon
>>> list(imports_in_code("import ;", filename="broken.py")
... )
Traceback (most recent call last):
  ...
SyntaxError: invalid syntax (broken.py, line 1)
```

### tec.imports.imports_under_folder(src, \*, path_filt=None, on_parse_error=<function warn_of_parse_error>)

Generate the [`ImportInfo`](#tec.imports.ImportInfo) of every `.py` file under `src`.

* **Parameters:**
  * **src** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Anything `PyFilesReader` accepts: a folder path,
    a module or package object, or the path of an `__init__.py` file.
  * **path_filt** ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`bool`](https://docs.python.org/3/builtins/functions.html#bool)]]) – Optional predicate on the store’s (relative) file paths, to
    narrow down the files that are parsed. `None` means “all `.py` files”.
  * **on_parse_error** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`SyntaxError`](https://docs.python.org/3/builtins/exceptions.html#SyntaxError), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`None`](https://docs.python.org/3/builtins/constants.html#None)]) – What to do with a file that doesn’t parse. Called with
    the `SyntaxError` and the path. See [`raise_parse_error()`](#tec.imports.raise_parse_error),
    [`warn_of_parse_error()`](#tec.imports.warn_of_parse_error) (the default) and [`ignore_parse_error()`](#tec.imports.ignore_parse_error).
* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)[[`ImportInfo`](#tec.imports.ImportInfo)]
* **Returns:**
  A generator of [`ImportInfo`](#tec.imports.ImportInfo).

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> with tempfile.TemporaryDirectory() as root:
...     _ = Path(root, 'a.py').write_text('import os\n')
...     _ = Path(root, 'b_test.py').write_text('import json\n')
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
```

### tec.imports.raise_parse_error(error, path)

`on_parse_error` strategy: let the `SyntaxError` propagate.

* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)

### tec.imports.warn_of_parse_error(error, path)

`on_parse_error` strategy: warn about the file, then skip it.

* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)
