# tec.packages

A few functions to investigate what objects can be imported from a module
(and the depth of the dot-path to import those objects directly).

The main function, print_top_level_diagnosis,
prints a diagnosis of the imports that can be optained from the (top level) module.
That is, those objects that can by imported by doing:

```text
from module import obj
```

though the object’s code may be several package levels down (say module.sub1.sub2.obj).

```text
>> import numpy, pandas, scipy
>> print_top_level_diagnosis(numpy)
--------- numpy ---------
601 objects can be imported from top level numpy:
  20 modules
  300 functions
  104 types

depth   count
0       163
1       406
2       2
3       29
4       1

>> print_top_level_diagnosis(pandas)
--------- pandas ---------
115 objects can be imported from top level pandas:
  12 modules
  55 functions
  40 types

depth   count
0       12
3       37
4       65
5       1

>> print_top_level_diagnosis(scipy)
--------- scipy ---------
582 objects can be imported from top level scipy:
  9 modules
  412 functions
  96 types

depth   count
0       61
1       395
2       4
3       122
```

### Functions

| `get_module_name`(package[, on_error])                                                         |                                                                                     |
|------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `obj_module_depth_counts`(module[, obj_filt])                                                  |                                                                                     |
| [`print_top_level_diagnosis`](#tec.packages.print_top_level_diagnosis)(module[, obj_filt]) | Prints a diagnosis of the imports that can be optained from the (top level) module. |
| `read_requirements`(requirements_file)                                                         |                                                                                     |
| `take_everything`(x)                                                                           |                                                                                     |
| `top_level_objs`(module[, obj_filt])                                                           |                                                                                     |

### tec.packages.print_top_level_diagnosis(module, obj_filt=<function <lambda>>)

Prints a diagnosis of the imports that can be optained from the (top level) module.
That is, those objects that can by imported by doing:

```text
from module import obj
```

though the object’s code may be several package levels down (say module.sub1.sub2.obj).

* **Parameters:**
  * **module** – The module (package) to analyze
  * **obj_filt** – The filter to apply (to the objects)

```text
>> import numpy, pandas, scipy
>> print_top_level_diagnosis(numpy)
--------- numpy ---------
601 objects can be imported from top level numpy:
  20 modules
  300 functions
  104 types

depth       count
0   163
1   406
2   2
3   29
4   1

>> print_top_level_diagnosis(pandas)
--------- pandas ---------
115 objects can be imported from top level pandas:
  12 modules
  55 functions
  40 types

depth       count
0   12
3   37
4   65
5   1

>> print_top_level_diagnosis(scipy)
--------- scipy ---------
582 objects can be imported from top level scipy:
  9 modules
  412 functions
  96 types

depth       count
0   61
1   395
2   4
3   122
```
