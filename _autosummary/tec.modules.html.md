# tec.modules

Tools to explore modules

### Functions

| `coerce_module_spec`(module_spec[, target, ...])                                              |                                                                                       |
|-----------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `dot_path_to_py_path`(dot_path[, root_module_str])                                            |                                                                                       |
| [`filepath_to_dotpath`](#tec.modules.filepath_to_dotpath)(filepath[, pkg_paths])   | Figures out a module dotpath from a filepath.                                         |
| `finding_objects_of_module_with_given_methods`(module)                                        |                                                                                       |
| `get_imported_module_paths`(module[, ...])                                                    |                                                                                       |
| [`is_from_module`](#tec.modules.is_from_module)(obj, module)                  | Check if an object "belongs" to a module.                                             |
| [`is_module_dotpath`](#tec.modules.is_module_dotpath)(dotpath)                   | Checks if a dotpath points to a module.                                               |
| [`loaded_module_from_dotpath_and_filepath`](#tec.modules.loaded_module_from_dotpath_and_filepath)(...) | Get module object from file path and module dotpath                                   |
| [`loaded_module_from_filepath`](#tec.modules.loaded_module_from_filepath)(filepath[, ...]) | Get module object from file path (resolving the dotpath automatically)                |
| `module_path`(module)                                                                         |                                                                                       |
| `module_spec_kind`(module_spec)                                                               |                                                                                       |
| `obj_to_dotpath`(obj)                                                                         |                                                                                       |
| `objects_of_module`(module[, max_levels])                                                     |                                                                                       |
| `py_path_to_dot_path`(py_path[, root_module_str])                                             |                                                                                       |
| [`second_party_names`](#tec.modules.second_party_names)(module[, obj_filt])       | Generator of module attribute names that point to object the module actually defines. |
| `submodules`(module[, on_error, prefix])                                                      |                                                                                       |

### Classes

| [`ModuleAllAttrsReader`](#tec.modules.ModuleAllAttrsReader)(module_src[, ...])          | Keys are module strings and values are {attr_name: attr_obj,...} dicts of the attributes of the module   |
|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| [`ModuleAttrsReader`](#tec.modules.ModuleAttrsReader)(module_src[, root_module_str]) | Like ModuleAllAttrsReader but will only give you attributes whose names don't start with an underscore.  |
| [`ModuleSpecKind`](#tec.modules.ModuleSpecKind)(\*values)                         |                                                                                                          |
| [`ModulesReader`](#tec.modules.ModulesReader)(module_src[, root_module_str])     | By store we mean key-value store.                                                                        |

### *class* tec.modules.ModuleAllAttrsReader(module_src, root_module_str='')

Bases: `Store`

Keys are module strings and values are {attr_name: attr_obj,…} dicts of the attributes of the module

#### is_valid_key(k, \*args, \_\_name='is_valid_key', \*\*kwargs)

`is_valid_key` on the inner key – see `mk_relative_path_store`.

#### validate_key(k, \*args, \_\_name='validate_key', \*\*kwargs)

`validate_key` on the inner key – see `mk_relative_path_store`.

### *class* tec.modules.ModuleAttrsReader(module_src, root_module_str='')

Bases: `Store`

Like ModuleAllAttrsReader but will only give you attributes whose names don’t start with an underscore.

#### is_valid_key(k, \*args, \_\_name='is_valid_key', \*\*kwargs)

`is_valid_key` on the inner key – see `mk_relative_path_store`.

#### validate_key(k, \*args, \_\_name='validate_key', \*\*kwargs)

`validate_key` on the inner key – see `mk_relative_path_store`.

### *class* tec.modules.ModuleSpecKind(\*values)

Bases: [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

### *class* tec.modules.ModulesReader(module_src, root_module_str='')

Bases: `Store`

By store we mean key-value store. This could be files in a filesystem, objects in s3, or a database. Where and
how the content is stored should be specified, but StoreInterface offers a dict-like interface to this.

```default
__getitem__ calls: _id_of_key                                       _obj_of_data
__setitem__ calls: _id_of_key                   _data_of_obj
__delitem__ calls: _id_of_key
__iter__    calls:                  _key_of_id
```

```pycon
>>> # Default store: no key or value conversion #####################################
>>> from dol import Store
>>> s = Store()
>>> s['foo'] = 33
>>> s['bar'] = 65
>>> assert list(s.items()) == [('foo', 33), ('bar', 65)]
>>> assert list(s.store.items()) == [('foo', 33), ('bar', 65)]  # see that the store contains the same thing
>>>
>>> #################################################################################
>>> # Now let's make stores that have a key and value conversion layer ##############
>>> # input keys will be upper cased, and output keys lower cased ###################
>>> # input values (assumed int) will be converted to ascii string, and visa versa ##
>>> #################################################################################
>>>
>>> def test_store(s):
...     s['foo'] = 33  # write 33 to 'foo'
...     assert 'foo' in s  # __contains__ works
...     assert 'no_such_key' not in s  # __nin__ works
...     s['bar'] = 65  # write 65 to 'bar'
...     assert len(s) == 2  # there are indeed two elements
...     assert list(s) == ['foo', 'bar']  # these are the keys
...     assert list(s.keys()) == ['foo', 'bar']  # the keys() method works!
...     assert list(s.values()) == [33, 65]  # the values() method works!
...     assert list(s.items()) == [('foo', 33), ('bar', 65)]  # these are the items
...     assert list(s.store.items()) == [('FOO', '!'), ('BAR', 'A')]  # but note the internal representation
...     assert s.get('foo') == 33  # the get method works
...     assert s.get('no_such_key', 'something') == 'something'  # return a default value
...     del(s['foo'])  # you can delete an item given its key
...     assert len(s) == 1  # see, only one item left!
...     assert list(s.items()) == [('bar', 65)]  # here it is
>>>
>>> # We can introduce this conversion layer in several ways. Here's a few... ######################
>>> # by subclassing ###############################################################################
>>> class MyStore(Store):
...     def _id_of_key(self, k):
...         return k.upper()
...     def _key_of_id(self, _id):
...         return _id.lower()
...     def _data_of_obj(self, obj):
...         return chr(obj)
...     def _obj_of_data(self, data):
...         return ord(data)
>>> s = MyStore(store=dict())  # note that you don't need to specify dict(), since it's the default
>>> test_store(s)
>>>
>>> # by assigning functions to converters ##########################################################
>>> class MyStore(Store):
...     def __init__(self, store, _id_of_key, _key_of_id, _data_of_obj, _obj_of_data):
...         super().__init__(store)
...         self._id_of_key = _id_of_key
...         self._key_of_id = _key_of_id
...         self._data_of_obj = _data_of_obj
...         self._obj_of_data = _obj_of_data
...
>>> s = MyStore(dict(),
...             _id_of_key=lambda k: k.upper(),
...             _key_of_id=lambda _id: _id.lower(),
...             _data_of_obj=lambda obj: chr(obj),
...             _obj_of_data=lambda data: ord(data))
>>> test_store(s)
>>>
>>> # using a Mixin class #############################################################################
>>> class Mixin:
...     def _id_of_key(self, k):
...         return k.upper()
...     def _key_of_id(self, _id):
...         return _id.lower()
...     def _data_of_obj(self, obj):
...         return chr(obj)
...     def _obj_of_data(self, data):
...         return ord(data)
...
>>> class MyStore(Mixin, Store):  # note that the Mixin must come before Store in the mro
...     pass
...
>>> s = MyStore()  # no dict()? No, because default anyway
>>> test_store(s)
>>>
>>> # adding wrapper methods to an already made Store instance #########################################
>>> s = Store(dict())
>>> s._id_of_key=lambda k: k.upper()
>>> s._key_of_id=lambda _id: _id.lower()
>>> s._data_of_obj=lambda obj: chr(obj)
>>> s._obj_of_data=lambda data: ord(data)
>>> test_store(s)
```

Note on defining your own “Mapping Views”.

When you do a `.keys()`, a `.values()` or `.items()` you’re getting a `MappingView`
instance; an iterable and sized container that provides some methods to access
particular aspects of the wrapped mapping.

If you need to customize the behavior of these instances, you should avoid
overriding the `keys`, `values` or `items` methods directly, but instead
override the `KeysView`, `ValuesView` or `ItemsView` classes that they use.

For more, see: [https://github.com/i2mint/dol/wiki/Mapping-Views](https://github.com/i2mint/dol/wiki/Mapping-Views)

#### is_valid_key(k, \*args, \_\_name='is_valid_key', \*\*kwargs)

`is_valid_key` on the inner key – see `mk_relative_path_store`.

#### validate_key(k, \*args, \_\_name='validate_key', \*\*kwargs)

`validate_key` on the inner key – see `mk_relative_path_store`.

### tec.modules.filepath_to_dotpath(filepath, pkg_paths=None)

Figures out a module dotpath from a filepath.
Checks the sys.path, removing the first common prefix if one is found,
then changes characters of the path components to make them valid identifier strings

### tec.modules.is_from_module(obj, module)

Check if an object “belongs” to a module.

```pycon
>>> import collections
>>> is_from_module(collections.ChainMap, collections)
True
>>> is_from_module(is_from_module, collections)
False
```

### tec.modules.is_module_dotpath(dotpath)

Checks if a dotpath points to a module.

### tec.modules.loaded_module_from_dotpath_and_filepath(dotpath, filepath)

Get module object from file path and module dotpath

### tec.modules.loaded_module_from_filepath(filepath, pkg_paths=None)

Get module object from file path (resolving the dotpath automatically)

### tec.modules.second_party_names(module, obj_filt=None)

Generator of module attribute names that point to object the module actually defines.

* **Parameters:**
  * **module** – Module (object)
  * **obj_filt** – Boolean function applied to object to filter it in
* **Returns:**

```pycon
>>> from tec import modules
>>> sorted(second_party_names(modules))[:5]
['DOTPATH', 'FILEPATH', 'FOLDERPATH', 'LOADED', 'ModuleAllAttrsReader']
>>> sorted(second_party_names(modules, callable))[:4]
['ModuleAllAttrsReader', 'ModuleAttrsReader', 'ModuleSpecKind', 'ModulesReader']
>>> sorted(second_party_names(modules, lambda obj: isinstance(obj, type)))
['ModuleAllAttrsReader', 'ModuleAttrsReader', 'ModuleSpecKind', 'ModulesReader']
```
