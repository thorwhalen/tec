
# tec
Tools to inspect python objects


To install:	```pip install tec```



# Examples

Generator of module attribute names that point to object the module actually defines.

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