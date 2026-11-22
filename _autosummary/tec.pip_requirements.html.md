# tec.pip_requirements

Tools to read and analyze pip requirements files as tabular data.

### Functions

| [`file_to_string`](#tec.pip_requirements.file_to_string)(filepath)   | returns the string contents of a pfile   |
|-----------------------------------------------------------------------------|------------------------------------------|
| `file_unique_identifiers`(f1, f2)                                           |                                          |
| `get_requirements_to_update_second_requirements_when_behind_first`(...)     |                                          |
| `print_requirements_comparison`(...)                                        |                                          |
| `requirement_file_to_df`(filepath)                                          |                                          |
| `requirements_comparison_df`(...)                                           |                                          |
| `requirements_comparison_df_only_when_different`(...)                       |                                          |
| `requirements_comparison_objects`(...)                                      |                                          |
| `rm_empty_version_entries`(comp_df)                                         |                                          |
| `updated_requirements_2_with_requirements_1_that_are_ahead`(...)            |                                          |
| `version_str_to_num`(version_str)                                           |                                          |

### tec.pip_requirements.file_to_string(filepath)

returns the string contents of a pfile
