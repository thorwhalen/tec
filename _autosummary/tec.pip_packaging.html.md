# tec.pip_packaging

Tools for pip packaging: create GitHub repos, look up PyPI versions, and
format packaging-related strings.

### Functions

| [`create_github_repo`](#tec.pip_packaging.create_github_repo)(name[, description, ...])   | Create a new github repository                           |
|-------------------------------------------------------------------------------------------------|----------------------------------------------------------|
| [`format_str_vals_of_dict`](#tec.pip_packaging.format_str_vals_of_dict)(d, \*[, ...])          |                                                          |
| [`get_last_pypi_version_number`](#tec.pip_packaging.get_last_pypi_version_number)(package[, ...])   | Return version of package on pypi.python.org using json. |
| `increment_version`(version_str)                                                                |                                                          |
| `my_setup`(\*\*setup_kwargs)                                                                    |                                                          |
| `next_version_for_package`(package[, url_template])                                             |                                                          |
| [`ujoin`](#tec.pip_packaging.ujoin)(\*args)                                  | Join strings with the url seperator (/).                 |

### Classes

| [`PartialFormatter`](#tec.pip_packaging.PartialFormatter)()   | A string formatter that won't complain if the fields are only partially formatted.   |
|-----------------------------------------------------------------------|--------------------------------------------------------------------------------------|

### *class* tec.pip_packaging.PartialFormatter

Bases: [`Formatter`](https://docs.python.org/3/library/string.html#string.Formatter)

A string formatter that won’t complain if the fields are only partially formatted.
But note that you will lose the spec part of your template (e.g. in {foo:1.2f}, you’ll loose the 1.2f
if not foo is given – but {foo} will remain).

### tec.pip_packaging.create_github_repo(name, description='', login_or_token=None, password=None)

Create a new github repository

#### NOTE
Requires github (pip install github)

### tec.pip_packaging.format_str_vals_of_dict(d, , max_formatting_loops=10, \*\*kwargs)

* **Parameters:**
  * **d**
  * **max_formatting_loops**
  * **kwargs**
* **Returns:**

```pycon
>>> d = {
...     'filepath': '{root}/{file}.{ext}',
...     'ext': 'txt'
... }
>>> format_str_vals_of_dict(d, root='ROOT', file='FILE')
{'filepath': 'ROOT/FILE.txt', 'ext': 'txt'}
```

Note that if the input mapping `d` and the kwargs have a conflict, the mapping version is used!

```pycon
>>> format_str_vals_of_dict(d, root='ROOT', file='FILE', ext='will_not_be_used')
{'filepath': 'ROOT/FILE.txt', 'ext': 'txt'}
```

But if you want to override an input mapping, you can – the usual way:

```pycon
>>> format_str_vals_of_dict(dict(d, ext='will_be_used'), root='ROOT', file='FILE')
{'filepath': 'ROOT/FILE.will_be_used', 'ext': 'will_be_used'}
```

If you don’t provide enough fields to satisfy all the format fields in the values of `d`,
you’ll be told to bugger off.

```pycon
>>> format_str_vals_of_dict(d, root='ROOT')
Traceback (most recent call last):
...
ValueError: I won't be able to complete that. You'll need to provide the values for:
  file
```

And it’s recursive…

```pycon
>>> d = {
...     'filepath': '{root}/{filename}',
...     'filename': '{file}.{ext}'
... }
>>> my_configs = {'root': 'ROOT', 'file': 'FILE', 'ext': 'EXT'}
>>> format_str_vals_of_dict(d, **my_configs)
{'filepath': 'ROOT/FILE.EXT', 'filename': 'FILE.EXT'}
```

# TODO: Could make the above work if filename is give, but not file nor ext! At least as an option.

### tec.pip_packaging.get_last_pypi_version_number(package, url_template='https://pypi.python.org/pypi/{package}/json')

Return version of package on pypi.python.org using json.

```text
> get_version('tec')
'0.0.7'
```

* **Parameters:**
  **package** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the package
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  A version (string

### tec.pip_packaging.ujoin(\*args)

Join strings with the url seperator (/).

Note that will add a / where it’s missing (as in between ‘[https://pypi.org](https://pypi.org)’ and ‘project/’),
and only use one if two consecutive tokens use respectively end and start with a /
(as in ‘project/’ and ‘/pipoke/’).

```pycon
>>> ujoin('https://pypi.org', 'project/', '/pipoke/')
'https://pypi.org/project/pipoke/'
```

Extremal cases

```pycon
>>> ujoin('https://pypi.org')
'https://pypi.org'
>>> ujoin('https://pypi.org/')
'https://pypi.org/'
>>> ujoin('')
''
>>> ujoin()
''
```
