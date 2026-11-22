# tec.misc.manage_pth_file

Utils to manage .pth file, which is read by environment to add paths to the python path.

At the time of writing this, the module is self-contained, only with python builtins and dol.

Works with 3.8+ (and perhaps lower).

### Functions

| `add_missing_items`(target, source)                                                         |                                                                       |
|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| [`add_missing_lines`](#tec.misc.manage_pth_file.add_missing_lines)(target[, source])        | Append the `source` lines missing from `target` to the `target` file. |
| `add_paths_of_packages_under_rootdir`(rootdir)                                              |                                                                       |
| [`add_to_pth_file`](#tec.misc.manage_pth_file.add_to_pth_file)(lines[, pth_filepath])     | Add some paths to the pth file (if they're not there already)         |
| `all_pth_file_names`([site_packages_folder])                                                |                                                                       |
| `filtered_pth_file_names`([...])                                                            |                                                                       |
| `first_pth_file_found`([site_packages_folder, ...])                                         |                                                                       |
| `first_site_packages_folder_found`()                                                        |                                                                       |
| `get_lines`(lines)                                                                          |                                                                       |
| `get_pth_filepath`([pth_filename, ...])                                                     |                                                                       |
| `get_site_packages_folder`([site_packages_folder])                                          |                                                                       |
| `lines_of_file`(filepath)                                                                   |                                                                       |
| `missing_items`(target, source)                                                             |                                                                       |
| [`mk_reclone_string`](#tec.misc.manage_pth_file.mk_reclone_string)(rootdir[, ...])          | Makes a file with a bunch of reclone instructions.                    |
| `print_pth_file_contents`()                                                                 |                                                                       |
| `reclone_pkg_commands`(pkg_rootdir)                                                         |                                                                       |
| `simple_run_command`(cmd, \*[, strip_output])                                               |                                                                       |
| [`target_and_missing_items`](#tec.misc.manage_pth_file.target_and_missing_items)(target[, source]) | Add source lines to target lines                                      |

### tec.misc.manage_pth_file.DFLT_FILENAME_FILT()

x._\_contains_\_(y) <==> y in x.

### tec.misc.manage_pth_file.add_missing_lines(target, source=())

Append the `source` lines missing from `target` to the `target` file.

`target` is a filepath: the missing lines are appended to it in place, and
the list of lines that were added is returned.

```pycon
>>> import os, tempfile
>>> path = os.path.join(tempfile.mkdtemp(), 'lines.txt')
>>> _ = open(path, 'w').write('one\ntwo\n\nthree')
>>> add_missing_lines(path, ['four', '', 'five'])
['four', 'five']
>>> print(open(path).read())
one
two

three
four
five
```

### tec.misc.manage_pth_file.add_to_pth_file(lines, pth_filepath=None)

Add some paths to the pth file (if they’re not there already)

* **Parameters:**
  **lines** – A ; or newline separated string of paths, or a filepath to a file containing these (one per line).

### tec.misc.manage_pth_file.mk_reclone_string(rootdir, save_in_filepath=None, filt=None)

Makes a file with a bunch of reclone instructions.
If `save_in_filepath` is given, it will save to that file.
You are to then chmod 744 the file and run it.

* **Parameters:**
  * **rootdir** – Directory within which to look for package folders
  * **save_in_filepath** – Save to this file
  * **filt** – Function to filter in package folder paths found in rootdir

### tec.misc.manage_pth_file.target_and_missing_items(target, source=())

Add source lines to target lines

```pycon
>>> target_and_missing_items(['one', 'two', '', 'three'], ['four', '', 'five'])
(['one', 'two', '', 'three'], ['four', 'five'])
```
