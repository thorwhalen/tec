from tec.peek import print_source, print_signature

from tec.modules import (
    loaded_module_from_dotpath_and_filepath,
    second_party_names,
    filepath_to_dotpath,
    get_imported_module_paths,
    ModulesReader,
    ModuleAllAttrsReader,
    ModuleAttrsReader,
)

from tec.pip_packaging import (
    create_github_repo,
    get_last_pypi_version_number,
    format_str_vals_of_dict,
    ujoin
)

from tec.packages import (
    print_top_level_diagnosis
)

from tec.stores import (
    file_contents_to_short_description,
    find_short_description_for_pkg,
    PkgReader,
    PkgFilesReader,  # TODO: Deprecate in favor of PyFilesReader
    PyFilesReader,
    builtins_py_files,
    sitepackages_py_files,
)

from tec.import_counting import (
    modules_imported,
    modules_imported_count,
    base_module_name
)

from tec.util import (
    extract_encoding_from_contents,
    get_encoding,
    decoding_problem_sentinel,
    decode_or_default,
    resolve_module_filepath,
    resolve_to_folder,
    resolve_module_contents,
)
