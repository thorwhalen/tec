"""Utils to manage .pth file, which is read by environment to add paths to the python path.

At the time of writing this, the module is self-contained, only with python builtins and dol.

Works with 3.8+ (and perhaps lower).

"""

import os
from operator import methodcaller
from pathlib import Path
from typing import Iterable, Union
import site
from functools import partial, lru_cache
from itertools import chain

# Pattern: mesh

Filepath = str  # + os.path.isfile
Lines = Union[Iterable[str], str, Filepath]

# DFLT_FILENAME_FILT = methodcaller('endswith', '.pth')
DFLT_FILENAME_FILT = {'oto.pth', 'conda.pth', 'custom.pth'}.__contains__


def lines_of_file(filepath):
    return Path(filepath).read_text().splitlines()


def get_lines(lines: Lines):
    if isinstance(lines, str):
        if os.path.isfile(lines):
            filepath = lines
            return lines_of_file(lines)
        elif ';' in lines:
            semicolumn_seperated_content = lines
            return list(map(str.strip, semicolumn_seperated_content.split(';')))
        else:
            file_content = lines
            return file_content.splitlines()
    else:
        assert isinstance(
            lines, Iterable
        ), f'lines should be a filepath, file content string or iterable of lines'
        return lines


def missing_items(target: Iterable, source: Iterable):
    return [x for x in source if x not in target]


def add_missing_items(target: Iterable, source: Iterable):
    return list(target) + missing_items(target, source)


def target_and_missing_items(target: Lines, source: Lines = ()):
    """Add source lines to target lines
    >>> target_and_missing_items(['one', 'two', '', 'three'], ['four', '', 'five'])
    (['one', 'two', '', 'three'], ['four', 'five'])
    """
    target, source = map(get_lines, [target, source])
    return target, missing_items(target, source)


def add_missing_lines(target: Filepath, source: Lines = ()):
    """Add source lines to target lines
    >>> _add_missing_lines(['one', 'two', '', 'three'], ['four', '', 'five'])
    ['one', 'two', '', 'three', 'four', 'five']
    """
    target_lines, missing_lines = target_and_missing_items(target, source)
    Path(target).write_text('\n'.join(target_lines + missing_lines))
    return missing_lines


def first_site_packages_folder_found():
    return site.getsitepackages()[0]


def get_site_packages_folder(site_packages_folder=None):
    if site_packages_folder is None:
        return first_site_packages_folder_found()


def all_pth_file_names(site_packages_folder=None):
    site_packages_folder = site_packages_folder or get_site_packages_folder()
    return os.listdir(site_packages_folder)


def filtered_pth_file_names(
    site_packages_folder=None, filename_filt=DFLT_FILENAME_FILT
):
    site_packages_folder = site_packages_folder or get_site_packages_folder()
    return list(filter(filename_filt, all_pth_file_names(site_packages_folder)))


def first_pth_file_found(site_packages_folder=None, filename_filt=DFLT_FILENAME_FILT):
    return next(iter(filtered_pth_file_names(site_packages_folder, filename_filt)))


def get_pth_filepath(
    pth_filename=None, site_packages_folder=None, filename_filt=DFLT_FILENAME_FILT
):
    site_packages_folder = get_site_packages_folder(site_packages_folder)
    pth_filename = pth_filename or first_pth_file_found(
        site_packages_folder, filename_filt
    )
    return os.path.join(site_packages_folder, pth_filename)


def print_pth_file_contents():
    print(Path(get_pth_filepath()).read_text())


def add_to_pth_file(lines, pth_filepath=None):
    """
    Add some paths to the pth file (if they're not there already)

    :param lines: A ; or newline separated string of paths, or a filepath to a file containing these (one per line).

    """

    def remove_trailing_slash(x):
        if (x[-1] == '/') or (x[-1] == '\\'):
            x = x[:-1]
        return x

    lines = list(map(remove_trailing_slash, get_lines(lines)))
    pth_filepath = pth_filepath or get_pth_filepath()
    return add_missing_lines(pth_filepath, lines)


# ----------------------------------------------------------------------------------------------------------------------
# Look at local files

from dol import Files, filt_iter, wrap_kvs, Pipe, cache_iter
from dol.filesys import FileCollection
from pathlib import Path


def init_root(init_filepath):
    return str(Path(init_filepath).parent)


def pkg_root(init_filepath):
    return str(Path(init_filepath).parent.parent)


def init_file_of_pkg_root(root):
    p = Path(root)
    return str(p / p.name / '__init__.py')


def is_package_init(k):
    if not k.endswith('__init__.py'):
        return False
    path = Path(k)
    parent = path.parent
    grandparent = parent.parent
    return parent.name == grandparent.name and (grandparent / 'setup.py').is_file()


# TODO: A quicker Packages (therefore root_dirpaths_to_packages) this can be done with DirCollection
#  since here we look through all files to only filter for the name/name/__init__.py
Packages = Pipe(
    filt_iter(FileCollection, filt=is_package_init),
    wrap_kvs(key_of_id=pkg_root, id_of_key=init_file_of_pkg_root),
    cache_iter,
)

@lru_cache
def root_dirpaths_to_packages(rootdir):
    return list(Packages(rootdir))


def add_paths_of_packages_under_rootdir(rootdir, pth_filepath=None):
    pkg_paths = root_dirpaths_to_packages(rootdir)
    return add_to_pth_file(pkg_paths, pth_filepath)


## TODO. Repair. Didn't work: Last git clone gave me errors (only through ps, not through terminal)
# def reclone_pkg(pkg_rootdir):
#     import ps
#     if pkg_rootdir[-1] != os.path.sep:
#         pkg_rootdir += os.path.sep
#     c = f"--work-tree {pkg_rootdir} --git-dir {pkg_rootdir}.git remote get-url origin"
#     url = ps.git(c).decode()
#     print(url)
#     ps.rm(f"-rf {pkg_rootdir}")
#     ps.git(f"clone {url} {pkg_rootdir}")

def simple_run_command(cmd, *, strip_output=True):
    with os.popen(cmd) as stream:
        output = stream.read()
    if strip_output:
        output = output.strip()
    return output

def reclone_pkg_commands(pkg_rootdir):
    import ps

    if pkg_rootdir[-1] != os.path.sep:
        pkg_rootdir += os.path.sep
    url = simple_run_command(f"git --work-tree {pkg_rootdir} --git-dir {pkg_rootdir}.git remote get-url origin")

    yield 'echo "----------------------------------------------------"'
    yield f'echo "{pkg_rootdir}"'
    yield f'rm -rf "{pkg_rootdir}"'
    yield f'git clone {url} "{pkg_rootdir}"'
    yield ''


def mk_reclone_string(rootdir, save_in_filepath=None, filt=None):
    """Makes a file with a bunch of reclone instructions.
    If ``save_in_filepath`` is given, it will save to that file.
    You are to then chmod 744 the file and run it.

    :param rootdir: Directory within which to look for package folders
    :param save_in_filepath: Save to this file
    :param filt: Function to filter in package folder paths found in rootdir
    """
    pkg_paths = list(filter(filt, root_dirpaths_to_packages(rootdir)))
    #     return pkg_paths
    s = '\n'.join(chain.from_iterable(map(reclone_pkg_commands, pkg_paths)))
    if save_in_filepath:
        return Path(save_in_filepath).write_text(s)
    else:
        return s


if __name__ == '__main__':
    from contextlib import suppress

    with suppress(ModuleNotFoundError):
        import argh

        argh.dispatch_commands(
            [
                add_to_pth_file,
                print_pth_file_contents,
                get_site_packages_folder,
                get_pth_filepath,
                root_dirpaths_to_packages,
                add_paths_of_packages_under_rootdir,
                mk_reclone_string,
            ]
        )
