# tec.misc

Misc tools.

#### NOTE
This content used to live in a `tec/misc.py` module, which was shadowed
by (and unreachable behind) this `tec/misc/` package. It was moved here so the
utilities are importable and so pytest can collect the package without an
import-file-mismatch collision.

### Functions

| [`infos_of_packages_under_rootdir`](#tec.misc.infos_of_packages_under_rootdir)(rootdir)   | Yields information about packages found recursively under rootdir   |
|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| `readme_path_for_setup_path`(setup_path)                                                    |                                                                     |

### tec.misc.infos_of_packages_under_rootdir(rootdir)

Yields information about packages found recursively under rootdir

> ### Examples

> ```python
>     from collections import defaultdict
>     from operator import itemgetter
>     rootdir = 'PROJECTS_ROOT_DIR'

>     project_info_for_group = defaultdict(list)
>     for group, *info in infos_of_packages_under_rootdir(rootdir):
>          project_info_for_group[group].append(info)

>     for group, projects in project_info_for_group.items():
>         print(f"----- {group} ---------")
>         for project_name, description, readme in projects:
>             one_line_description = description.replace('
> ', ' ')
>             print(f"{project_name}: {one_line_description}")
> ```

### Modules

| [`manage_pth_file`](tec.misc.manage_pth_file.html.md#module-tec.misc.manage_pth_file)   | Utils to manage .pth file, which is read by environment to add paths to the python path.   |
|----------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
