# tec.snake_food_import_counting

Count and analyze module imports, snakefood-style (via static analysis).

### Functions

| [`base_module_imports_in_module_recursive`](#tec.snake_food_import_counting.base_module_imports_in_module_recursive)(module)   | Get a list of strings showing what base modules that are imported in a module, recursively.   |
|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| [`base_modules_used_in_module`](#tec.snake_food_import_counting.base_modules_used_in_module)(module)               | Get a list of strings showing what base modules that are imported in a module.                |
| `get_filepath_iterator`(root_folder[, ...])                                                        |                                                                                               |
| [`imports_in_module`](#tec.snake_food_import_counting.imports_in_module)(module)                         | Get a list of strings showing what is imported in a module.                                   |
| `iter_relative_files_and_folder`(root_folder)                                                      |                                                                                               |
| `pattern_filter`(pattern)                                                                          |                                                                                               |
| [`pip_licenses_df`](#tec.snake_food_import_counting.pip_licenses_df)([package_names, ...])             | Get a dataframe of pip packages and licences                                                  |
| `recursive_file_walk_iterator_with_filepath_filter`(...)                                           |                                                                                               |
| `recursive_file_walk_iterator_with_name_filter`(...)                                               |                                                                                               |
| `requirements_packages_in_module`(module[, ...])                                                   |                                                                                               |

### tec.snake_food_import_counting.base_module_imports_in_module_recursive(module)

Get a list of strings showing what base modules that are imported in a module, recursively.
It’s the recursive version of the base_modules_used_in_module function.
Recursive in the sense that if module is a package module (i.e. containing a \_\_init_\_.py and further submodules),
the base_modules_used_in_module function will be applied to all .py files under the mother folder.
Function returns a count (Counter object) of the number of modules where each base module was found.

* **Parameters:**
  * **module** – An actual module object the file of the module (as given by inspect.getfile(module)
  * **module_names** – Modules to filter for.
    None: Will grab all modules
    A list or tuple: Of modules to grab
    If not will assume module_names is a regex to apply to find module names
* **Returns:**

### tec.snake_food_import_counting.base_modules_used_in_module(module)

Get a list of strings showing what base modules that are imported in a module.

* **Parameters:**
  **module** – An actual module object the file of the module (as given by inspect.getfile(module)
* **Returns:**
  A list of strings showing the imported base modules (i.e. the X of import X.Y.Z or from X.Y import Z).

#### NOTE
Requires having snakefood installed:
[http://furius.ca/snakefood/doc/snakefood-doc.html#installation](http://furius.ca/snakefood/doc/snakefood-doc.html#installation)

```pycon
>>> base_modules_used_in_module(__file__)
['StringIO', 'collections', 'inspect', 'numpy', 'os', 'pandas', 're', 'subprocess', 'ut']
```

### tec.snake_food_import_counting.imports_in_module(module)

Get a list of strings showing what is imported in a module.

* **Parameters:**
  **module** – An actual module object the file of the module (as given by inspect.getfile(module)
* **Returns:**
  A list of strings showing the imported objects (modules, functions, variables, classes…)

#### NOTE
Requires having snakefood installed:
[http://furius.ca/snakefood/doc/snakefood-doc.html#installation](http://furius.ca/snakefood/doc/snakefood-doc.html#installation)

You may want to use `imports_in_py_content(py_content)` on the actual string content itself.

# >>> print(’n’.join(imports_in_module(_\_file_\_)))  # doctest: +SKIP
# StringIO.StringIO
# collections.Counter
# inspect
# numpy.unique
# os
# pandas
# re
# subprocess
# ut.pfile.iter.get_filepath_iterator
# ut.util.code.packages.get_module_name
# ut.util.code.packages.read_requirements

### tec.snake_food_import_counting.pip_licenses_df(package_names=None, include_module_name=True, on_module_search_error=None)

Get a dataframe of pip packages and licences

* **Returns:**
