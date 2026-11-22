# tec.stores

(dol) stores (i.e. mapping interfaces) to access python files

### Functions

| `file_contents_to_short_description`(file_contents)                                           |                                                                                                           |
|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| [`find_short_description_for_pkg`](#tec.stores.find_short_description_for_pkg)(s)            | Generator of (pkg_name, short_description) pairs (using the header comments of init files as description) |
| [`py_files_with_contents_matching_pattern`](#tec.stores.py_files_with_contents_matching_pattern)(...) | Yields (relative) file paths of .py files whose contents match pattern.                                   |

### tec.stores.find_short_description_for_pkg(s)

Generator of (pkg_name, short_description) pairs (using the header comments of init files as description)

### tec.stores.py_files_with_contents_matching_pattern(files_src, pattern)

Yields (relative) file paths of .py files whose contents match pattern.

* **Parameters:**
  * **files_src** – Source of files. Module, package, folder, or \_\_init_\_.py file.
  * **pattern** – regular expression (string or re.Pattern object)

Let’s see what modules of asyncio contain the “import io” string:

```pycon
>>> import asyncio
>>> set(py_files_with_contents_matching_pattern(asyncio, 'import io')).issuperset(
...     {'proactor_events.py', 'unix_events.py'})
True
```
