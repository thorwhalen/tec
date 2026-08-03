
# tec
Tools to inspect python objects


To install:	```pip install tec```


# Examples

## Counting imported names

### Quickly (``tec.import_counting``)

``modules_imported`` is a generator of module names from obj. 
It uses string parsing, so is not as accurate as some other methods, but is fast and flexible, 
and doesn't require actually running any of the code analyzed.
    
```python
>>> from tec import modules_imported
>>> import os.path  # single module
>>> list(modules_imported(os.path))  # list of names in the order they were found
['os', 'sys', 'stat', 'genericpath', 'genericpath', 'pwd', 'pwd', 're', 're']
>>> import os  # package with several modules
>>> from collections import Counter
>>> Counter(modules_imported(os, only_base_name=True)).most_common()  #doctest: +ELLIPSIS
[('nt', 5), ('posix', 4), ... ('warnings', 1), ('subprocess', 1)]
```

### Accurately (``tec.imports``)

When accuracy matters more than speed, ``tec.imports`` parses the code with the
standard library's ``ast``, so import-looking strings, comments and line
continuations can't fool it. Each import comes back as an ``ImportInfo``
(``name``, ``filename``, ``lineno``, ``level``).

```python
>>> from tec import imports_in_code, count_imports
>>> [imp.name for imp in imports_in_code("import os\nfrom json import dumps")]
['os', 'json.dumps']
>>> count_imports(some_package_or_folder).most_common(3)  # doctest: +SKIP
[('os', 12), ('dol', 7), ('re', 5)]
```

``count_imports`` (and ``imports_under_folder``) take a folder path, a module
object, a package, or an ``__init__.py`` path; what gets counted is decided by the
``import_key`` argument, which defaults to the top-level package name.

> **Note.** ``tec.imports`` replaces ``tec.findimports``, which held a vendored copy
> of the GPL-2.0-or-later ``findimports`` project -- incompatible with ``tec``'s own
> Apache-2.0 licence, and therefore removed. ``tec.findimports`` remains as a
> deprecated forwarding layer. The module-*graph* part of that old API has no ``tec``
> equivalent; install the upstream project yourself if you need it.

## Modules

```pydocstring
>>> from tec import modules
>>> sorted(modules.second_party_names(modules))[:5]
['DOTPATH', 'FILEPATH', 'FOLDERPATH', 'LOADED', 'ModuleSpecKind']
>>> sorted(modules.second_party_names(modules, callable))[:4]
['ModuleSpecKind', 'coerce_module_spec', 'filepath_to_dotpath', 'finding_objects_of_module_with_given_methods']
>>> sorted(modules.second_party_names(modules, lambda obj: isinstance(obj, type)))
['ModuleSpecKind']
```

## Packages

A few functions to investigate what objects can be imported from a module
(and the depth of the dot-path to import those objects directly).

The main function, ``print_top_level_diagnosis``,
prints a diagnosis of the imports that can be optained from the (top level) module.
That is, those objects that can by imported by doing:
```
from module import obj
```
though the object's code may be several package levels down (say module.sub1.sub2.obj).


```pydocstring
>> import numpy, pandas, scipy
>> print_top_level_diagnosis(numpy)
--------- numpy ---------
601 objects can be imported from top level numpy:
  20 modules
  300 functions
  104 types

depth	count
0	163
1	406
2	2
3	29
4	1

>> print_top_level_diagnosis(pandas)
--------- pandas ---------
115 objects can be imported from top level pandas:
  12 modules
  55 functions
  40 types

depth	count
0	12
3	37
4	65
5	1

>> print_top_level_diagnosis(scipy)
--------- scipy ---------
582 objects can be imported from top level scipy:
  9 modules
  412 functions
  96 types

depth	count
0	61
1	395
2	4
3	122
```


## Peek

```pydocstring
>>> from tec.peek import print_signature
>>> print_signature(print_signature)
func
sep: Union[str, NoneType] = '\\n'
prefix: str = ''
suffix: str = ''
>>> print_signature(print_signature, None)
(func, sep: Union[str, NoneType] = '\\n', prefix: str = '', suffix: str = '')
>>> print_signature(print_signature, '\\n * ', prefix=' * ', suffix='\\n')
 * func
 * sep: Union[str, NoneType] = '\\n'
 * prefix: str = ''
 * suffix: str = ''
<BLANKLINE>
```