# tec.util

Builtin tec utils

### Functions

| [`bitmap_selection`](#tec.util.bitmap_selection)(iterable, selector)              | Select items of an iterable with items of a selector sequence of the same size.                                  |
|----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| `ddir`(o)                                                                                          |                                                                                                                  |
| `decode_or_default`(b[, dflt, use_cchardet])                                                       |                                                                                                                  |
| `extract_encoding_from_contents`(content_bytes)                                                    |                                                                                                                  |
| [`find`](#tec.util.find)(query, items[, query_matches_item, ...])     | Find anything in an iterable of items, based on your query language of choice.                                   |
| [`find_objects`](#tec.util.find_objects)(pattern, objects[, ...])             | Find strings matching a given pattern, possibly sorting them in a specific way.                                  |
| [`func_fanout`](#tec.util.func_fanout)(\*args, funcs, \*\*kwargs)            | Util to make a function that applies multiple functions to a single input.                                       |
| `get_encoding`(content_bytes[, use_cchardet])                                                      |                                                                                                                  |
| `identity`(x)                                                                                      |                                                                                                                  |
| [`import_and_add_if_available`](#tec.util.import_and_add_if_available)(obj_name, ...[, ...]) | Import object named `obj_name` from module named `module_name`, sticking it in scope (a dict, usually locals()). |
| [`name_and_object_pairs`](#tec.util.name_and_object_pairs)(objects[, ...])             | Get (name, object) pairs from source of objects                                                                  |
| [`print_signatures`](#tec.util.print_signatures)(obj[, object_to_strings, sep])   | Prints information on callable attributes of obj (module, class, ...)                                            |
| `resolve_module_contents`(module_spec[, dflt, ...])                                                |                                                                                                                  |
| [`signature_strings`](#tec.util.signature_strings)(objects[, object_to_strings])   | A generator of strings describing the callables in obj (module, class, ...)                                      |

### tec.util.bitmap_selection(iterable, selector)

Select items of an iterable with items of a selector sequence of the same size.
The selector items should be, or resolve to, a `bool`.

```pycon
>>> list(bitmap_selection([2, 4, 6, 8], [True, False, True, False]))
[2, 6]
>>> tuple(bitmap_selection(range(5), [1, 0, None, '', 'blah']))
(0, 4)
```

### tec.util.find(query, items, query_matches_item=<built-in function eq>, query_key=<function identity>, item_key=<function identity>)

Find anything in an iterable of items, based on your query language of choice.

Is limited to no query or items type. All you need to do is define what a match
of a query and item is, through the `query_matches_item` function.

Example use:

```pycon
>>> items = [
...     'www.google.com',
...     'www.yahoo.com',
...     'www.harvard.edu',
...     'web.mit.edu',
... ]
>>> list(find('www.harvard.edu', items))
['www.harvard.edu']
>>> list(find('oo', items, query_matches_item=lambda q, i: q in i))
['www.google.com', 'www.yahoo.com']
>>> list(find('edu', items, item_key=lambda item: item.split('.')[-1]))
['www.harvard.edu', 'web.mit.edu']
```

Often you may want to use functools.partials to make a searcher you can reuse
without having to specify the particulars of the search (including or not the
items you want to search).

```pycon
>>> from functools import partial
>>> finder = partial(find, items=items, query_matches_item=lambda q, i: q in i,
...                    query_key=str.lower, item_key=str.lower)
>>> list(finder('GOOGLE'))
['www.google.com']
```

Note that the `query_matches_item` is sufficient.
For example, in the above we could have done it like this:

```pycon
>>> list(find('GOOGLE', items, lambda q, i: q.lower() in i.lower()))
['www.google.com']
```

There’s never any actual need for the key functions, but they’re provided for
convenience and reuse of general `query_matches_item` functions.

### tec.util.find_objects(pattern, objects, objects_to_strings=<function \_if_not_iterable_get_attributes>, \*, key=None)

Find strings matching a given pattern, possibly sorting them in a specific way.

* **Parameters:**
  * **pattern** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The pattern to search (string representing a regular expression).
  * **objects** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – An iterable of strings or an object that will resolve in one.
  * **objects_to_strings** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`Any`](https://docs.python.org/3/library/typing.html#typing.Any)], [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]) – The function that resolves the `objects` input
    (which is not even necessarily an iterable) into an iterable of strings.
  * **key** – If not None, will be used to sort matched objects.
    `key` will be applied to objects of type `re.Match`;
    see [https://docs.python.org/3/library/re.html#match-objects](https://docs.python.org/3/library/re.html#match-objects) to get an idea of
    how to define the right key function.
    If `key` is an iterable (“of callables”, assumed), make an
    aggregate of these functions that will return a tuple of the sort keys.
    This is akin to sorting by one columns primarly, a second secondarily, etc.
* **Returns:**
  A generator of matched strings.

```pycon
>>> kwargs = dict(
...     pattern='li',
...     objects='bob and lilabet like to play with alice',
...     objects_to_strings=str.split,
... )
>>> list(find_objects(**kwargs))
['lilabet', 'like', 'alice']
```

Sort the results in reverse length of string:

```pycon
>>> list(find_objects(**kwargs, key=lambda x: -len(x.string)))
['lilabet', 'alice', 'like']
```

Sort the results according to how early in the string the match happens:

```pycon
>>> from operator import methodcaller
>>> list(find_objects(**kwargs, key=methodcaller('span')))
['lilabet', 'like', 'alice']
```

The same as above, but with secondary “length” sorting:

```pycon
>>> tuple(  # for a change!
...     find_objects(**kwargs, key=[methodcaller('span'), lambda x: len(x.string)])
... )
('like', 'lilabet', 'alice')
```

### tec.util.func_fanout(\*args, funcs, \*\*kwargs)

Util to make a function that applies multiple functions to a single input.
Note that the function returns a generator that needs to be “consumed” to actually
get the outputs of the function.

`func_fanout` is meant to be used with `functools.partial` to “make” the
desired function, such as:

```pycon
>>> from functools import partial
>>> f = partial(func_fanout, funcs=[
...     lambda x, y: x + y,
...     lambda x, y: x * y,
... ])
>>> list(f(2, 3))
[5, 6]
>>> tuple(f(3, y=4))
(7, 12)
```

<!-- seealso: ``i2.multi_object.FuncFanout`` for a more involved version of this. -->

### tec.util.import_and_add_if_available(obj_name, module_name, as_name=None, scope=None, if_already_in_scope=None, if_not_found=None)

Import object named `obj_name` from module named `module_name`, sticking it
in scope (a dict, usually locals()).

* **Parameters:**
  * **scope** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)) – A dict where the object will be stored (if found). Usually locals().
  * **obj_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The name of the object to import
  * **module_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – The name of the module to import the object from
  * **as_name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – The name to use in the scope. Defaults to `obj_name`
  * **if_already_in_scope** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – If not None, should be a `(scope, as_name, obj)`
    callable that will provide the return value if `as_name` is already in the
    scope.
    This is to be able to overwrite the default of simply doing a
    `scope[as_name] = obj` (having the net effect of resolving name conflicts
    by a “last one seen wins” strategy.
  * **if_not_found** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable) | [`None`](https://docs.python.org/3/builtins/constants.html#None)) – If not None, should be a `(obj_name, module_name)` callable
    that will provide the return value if `obj_name` is not found in
    `module_name`.
* **Returns:**

```pycon
>>> from functools import partial  # not necessary, but represents use case
>>> scope = dict()  # you'd usually put locals() here
>>> acquire = partial(import_and_add_if_available, scope=scope)
>>> acquire('join', 'os.path')
True
>>> acquire('isfile', 'os.path', as_name='check_if_file_exists')
True
>>> acquire('not_in_os_path', 'os.path')  # returns False: not found in os.path
False
>>> acquire('object', 'does.not.exist')  # returns None: the module_name not found
>>> import os
>>> assert (scope ==
...     {'join': os.path.join, 'check_if_file_exists': os.path.isfile}
... )
```

See in the above that neither `'not_in_os_path'` nor `'object'` are in
`scope`. They were simply skipped.

### tec.util.name_and_object_pairs(objects, objects_to_iterable=<function \_attribute_name_object_pairs>, \*, name_filt=<function \_not_prefixed_by_underscore>, obj_filt=<built-in function callable>, name_of_obj=operator.attrgetter('_\_name_\_'))

Get (name, object) pairs from source of objects

* **Parameters:**
  * **objects** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The source we want to extract name and object pairs from.
    Could be an explicit list of pairs, or a single object (like a module)
    from which we’ll generate these (using `objects_to_iterable`)
  * **objects_to_iterable** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)]) – If the input `objects` isn’t already an iterable,
    the function to make it so
  * **name_filt** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`bool`](https://docs.python.org/3/builtins/functions.html#bool)]) – A condition on the name
  * **obj_filt** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`bool`](https://docs.python.org/3/builtins/functions.html#bool)]) – A condition on the object
  * **name_of_obj** ([`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`Any`](https://docs.python.org/3/library/typing.html#typing.Any)], [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – when an element of the iterable isn’t a (name, obj) pair,
    the function to get the name of a the object.

Get method names of the dict class:

```pycon
>>> next(zip(*name_and_object_pairs(dict)))
('clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop', 'popitem', 'setdefault', 'update', 'values')
```

Get only those names of dict methods that contain the string ‘keys’:

```pycon
>>> next(zip(*name_and_object_pairs(dict, name_filt=lambda x: 'keys' in x)))
('fromkeys', 'keys')
```

### tec.util.print_signatures(obj, object_to_strings=<function <lambda>>, sep='\\n \* ')

Prints information on callable attributes of obj (module, class, …)

### tec.util.signature_strings(objects, object_to_strings=<function <lambda>>)

A generator of strings describing the callables in obj (module, class, …)
