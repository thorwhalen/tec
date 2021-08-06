"""Misc tools"""

import os

from dol.filesys import FileStringReader

readme_path_for_setup_path = (
    lambda setup_path: setup_path[: -len("setup.cfg")] + "README.md"
)


def infos_of_packages_under_rootdir(rootdir):
    """Yields information about packages found recursively under rootdir

    Examples:

    ```python
    from collections import defaultdict
    from operator import itemgetter
    rootdir = 'PROJECTS_ROOT_DIR'

    project_info_for_group = defaultdict(list)
    for group, *info in infos_of_packages_under_rootdir(rootdir):
         project_info_for_group[group].append(info)

    for group, projects in project_info_for_group.items():
        print(f"----- {group} ---------")
        for project_name, description, readme in projects:
            one_line_description = description.replace('\n', ' ')
            print(f"{project_name}: {one_line_description}")
    ```

    """
    from config2py import ConfigReader  # pip install config2py

    if not rootdir.endswith(os.path.sep):
        rootdir += os.path.sep
    rootdir_len = len(rootdir)
    file_reader = FileStringReader(rootdir)

    for setup_path in filter(lambda f: f.endswith("setup.cfg"), file_reader):
        readme_path = readme_path_for_setup_path(setup_path)
        if readme_path in file_reader:
            try:
                project_relpath = setup_path[rootdir_len : -len("setup.cfg")]
                *rel_path, project_name, _ = project_relpath.split(os.path.sep)
                description = ConfigReader(setup_path)["metadata"].get("description", "")
                readme = file_reader[readme_path]
                yield os.path.sep.join(rel_path), project_name, description, readme
            except Exception as e:
                print(f"Skipping {setup_path} because of error: {e}")
