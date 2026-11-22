# tec.peek

Peek at Python objects: print their source code and signatures.

### Functions

| `aval_gen`(o[, filt])                                                                         |                                             |
|-----------------------------------------------------------------------------------------------|---------------------------------------------|
| `not_dunder`(a)                                                                               |                                             |
| [`print_signature`](#tec.peek.print_signature)(func[, sep, prefix, suffix]) | Print the signature of a callable           |
| [`print_source`](#tec.peek.print_source)(o[, start, end, doc])           | Prints the source code of the input object. |
| `show_attrs`(o[, filt])                                                                       |                                             |
| `submodule_path_strings`(module)                                                              |                                             |

### tec.peek.print_signature(func, sep='\\n', prefix='', suffix='')

Print the signature of a callable

* **Parameters:**
  * **func** – Callable to print the signature of
  * **sep** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – If None, will print the signature as inspect.signature would.
    If a string, will use the string to separate the parameter specifications

```pycon
>>> print_signature(print_signature)
func
sep: str | None = '\n'
prefix: str = ''
suffix: str = ''
>>> print_signature(print_signature, None)
(func, sep: str | None = '\n', prefix: str = '', suffix: str = '')
>>> print_signature(print_signature, '\n * ', prefix=' * ', suffix='\n')
 * func
 * sep: str | None = '\n'
 * prefix: str = ''
 * suffix: str = ''
```

### tec.peek.print_source(o, start=None, end=None, doc=True)

Prints the source code of the input object. Can specify lines to print with start and end.

```pycon
>>> print_source(print_source, 0, 1)
def print_source(o, start=None, end=None, doc=True):

>>> print_source(print_source, 11)
    _lines, _ = getsourcelines(o)
    print(''.join(_lines[slice(start, end)]))
```
