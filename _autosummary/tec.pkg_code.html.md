# tec.pkg_code

Tools to analyze local code files for packages.

#### NOTE
Assumes these packages are in the format:

package/  # aka project root
: setup.py
  setup.cfg
  README.md
  package/  # aka package directory
  <br/>
  > \_\_init_\_.py
  > module1.py
  > module2.py
  > …

### Functions

| `Packages`(rootdir[, max_levels, only_if_has_init])   |    |
|-------------------------------------------------------|----|
| `dir_whose_parent_has_same_name`(k)                   |    |
| `folder_has_init`(path)                               |    |
| `init_file_of_pkg_root`(root)                         |    |
| `init_root`(init_filepath)                            |    |
| `is_package_directory`(path)                          |    |
| `is_package_init`(k)                                  |    |
| `is_project_root`(path)                               |    |
| `package_directory_of_project_root`(path)             |    |
| `package_root_dirs`(rootdir[, max_levels, ...])       |    |
| `pkg_root`(init_filepath)                             |    |
| `root_dirpaths_to_packages`(rootdir[, ...])           |    |
