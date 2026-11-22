# tec.findimports

Deprecated compatibility layer – use [`tec.imports`](tec.imports.html.md#module-tec.imports) instead.

`tec` used to ship, under this module name, a vendored (lightly edited) copy of
the third party `findimports` project. That copy was distributed under the
GPL-2.0-or-later, which is incompatible with `tec`’s own Apache-2.0 terms, so it
has been removed.

What replaces it:

- Import finding is now done by [`tec.imports`](tec.imports.html.md#module-tec.imports), an independent implementation
  written against the standard library’s `ast`. The functions of this module
  simply forward to it.
- The names that had no `tec` equivalent – essentially the module *graph*
  machinery (`ModuleGraph`, `ImportFinder`, `Module`, …) – are gone. If
  you need them, install the upstream project yourself
  (`pip install findimports`), keeping in mind that doing so subjects your work
  to *its* licence rather than `tec`’s.

Importing this module emits a `DeprecationWarning`. Asking it for one of the
removed names raises an `AttributeError` that says what to do instead:

```pycon
>>> import tec.findimports as fi
>>> fi.ModuleGraph
Traceback (most recent call last):
  ...
AttributeError: ...
```

### Module Attributes

| [`REPLACEMENT_MODULE`](#tec.findimports.REPLACEMENT_MODULE)          | Module that supersedes this one.                                                         |
|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| [`UPSTREAM_ONLY_ADVICE`](#tec.findimports.UPSTREAM_ONLY_ADVICE)        | Advice for the names that only the (GPL) upstream project provides.                      |
| [`REMOVED_NAMES`](#tec.findimports.REMOVED_NAMES)               | Names the removed vendored implementation used to provide, mapped to what to do instead. |
| [`REMOVED_NAME_ERROR_TEMPLATE`](#tec.findimports.REMOVED_NAME_ERROR_TEMPLATE) | Template of the error raised when a removed name is requested.                           |
| [`DEPRECATION_MESSAGE`](#tec.findimports.DEPRECATION_MESSAGE)         | Message of the `DeprecationWarning` emitted when this module is imported.                |

### Functions

| [`count_imports`](#tec.findimports.count_imports)(rootdir[, pathfilt, ...])   | Deprecated alias of [`tec.imports.count_imports()`](tec.imports.html.md#tec.imports.count_imports).               |
|--------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| [`re_find_imports`](#tec.findimports.re_find_imports)(rootdir[, pathfilt])      | Deprecated alias of [`tec.imports.imports_under_folder()`](tec.imports.html.md#tec.imports.imports_under_folder). |

### tec.findimports.DEPRECATION_MESSAGE *= 'tec.findimports is deprecated: use tec.imports instead. The vendored GPL-2.0-or-later implementation this module used to hold was removed (licence incompatibility); what is left is a thin forwarding layer.'*

Message of the `DeprecationWarning` emitted when this module is imported.

### tec.findimports.REMOVED_NAMES *= {'ImportFinder': 'use tec.imports.imports_in_code', 'ImportFinderAndNameTracker': 'use tec.imports.imports_in_code', 'Module': 'there is no tec equivalent; install the upstream (GPL-2.0-or-later) project with \`pip install findimports\` if you need it', 'ModuleCycle': 'there is no tec equivalent; install the upstream (GPL-2.0-or-later) project with \`pip install findimports\` if you need it', 'ModuleGraph': 'there is no tec equivalent; install the upstream (GPL-2.0-or-later) project with \`pip install findimports\` if you need it', 'ModuleImportsBase': 'use tec.imports.ModuleImports', 'ModulesColl': 'use tec.imports.ModuleImports (or tec.modules.ModulesReader)', 'Scope': 'there is no tec equivalent', 'adjust_lineno': 'there is no tec equivalent; ast node line numbers are used as is', 'file_sep': 'use os.path.sep', 'find_imports_and_track_names': 'use tec.imports.find_imports', 'iter_relative_files_and_folder': 'use tec.stores.PyFilesReader', 'main': 'there is no tec equivalent; this module has no command line interface', 'modname_to_modobj': 'use tec.imports.ModuleImports', 'modobj_to_modname': 'use tec.imports.ModuleImports', 'pattern_filter': 'use tec.stores.PyFilesReader (or a plain re.compile(...).match)', 'quote': 'there is no tec equivalent; it was a graphviz-output helper', 'recursive_file_walk_iterator_with_filepath_filter': 'use tec.stores.PyFilesReader'}*

Names the removed vendored implementation used to provide, mapped to what to do
instead. Kept as data (rather than in the error-raising code) so that the
“what happened to X?” answers are a single, extensible source of truth.

### tec.findimports.REMOVED_NAME_ERROR_TEMPLATE *= "{module}.{name} was removed: it came from a vendored GPL-2.0-or-later copy of the third party \`findimports\` project, which was incompatible with tec's Apache-2.0 licence. Instead, {advice}."*

Template of the error raised when a removed name is requested.

### tec.findimports.REPLACEMENT_MODULE *= 'tec.imports'*

Module that supersedes this one.

### tec.findimports.UPSTREAM_ONLY_ADVICE *= 'there is no tec equivalent; install the upstream (GPL-2.0-or-later) project with \`pip install findimports\` if you need it'*

Advice for the names that only the (GPL) upstream project provides.

### tec.findimports.count_imports(rootdir, pathfilt=<function \_is_py_path>, import_obj_func=<function base_package_of>)

Deprecated alias of [`tec.imports.count_imports()`](tec.imports.html.md#tec.imports.count_imports).

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> with tempfile.TemporaryDirectory() as root:
...     _ = Path(root, 'a.py').write_text('import os.path\nimport json\n')
...     counts = count_imports(root)
>>> sorted(counts.items())
[('json', 1), ('os', 1)]
```

### tec.findimports.re_find_imports(rootdir, pathfilt=<function \_is_py_path>)

Deprecated alias of [`tec.imports.imports_under_folder()`](tec.imports.html.md#tec.imports.imports_under_folder).

Note the (harmless for the default) semantic difference: `pathfilt` is now
applied to store-relative paths, not to absolute ones.

```pycon
>>> import tempfile
>>> from pathlib import Path
>>> with tempfile.TemporaryDirectory() as root:
...     _ = Path(root, 'a.py').write_text('import os\n')
...     names = [imp.name for imp in re_find_imports(root)]
>>> names
['os']
```
