import re
import inspect
import os

DFLT_USE_CCHARDET = True

try:
    import cchardet as chardet
except ModuleNotFoundError:
    try:
        import chardet
    except ModuleNotFoundError:
        DFLT_USE_CCHARDET = False

encoding_spec_re = re.compile(b"-*- coding: (.+) -*-")


import operator
from typing import Any, Callable, Iterable

Query = Any
Item = Any

def identity(x):
    return x


def find(
    query: Any,
    items: Iterable[Item],
    query_matches_item: Callable[[Query, Item], bool]=operator.eq,
    query_key: Callable[[Query], Query] = identity,
    item_key: Callable[[Item], Item] = identity,
):
    """Find anything in an iterable of items, based on your query language of choice.

    Is limited to no query or items type. All you need to do is define what a match
    of a query and item is, through the `query_matches_item` function.

    Example use:

    >>> items = [
    ...     'www.google.com',
    ...     'www.yahoo.com',
    ...     'www.harvard.edu',
    ...     'web.mit.edu',
    ... ]
    >>> list(find('www.harvard.edu', items))
    ['www.harvard.edu']
    >>> list(find('oo', items, query_matches_item=lambda q, i: q in i))
    ['www.google.com', 'www.yahoo.com']
    >>> list(find('edu', items, item_key=lambda item: item.split('.')[-1]))
    ['www.harvard.edu', 'web.mit.edu']

    Often you may want to use functools.partials to make a searcher you can reuse
    without having to specify the particulars of the search (including or not the
    items you want to search).

    >>> from functools import partial
    >>> finder = partial(find, items=items, query_matches_item=lambda q, i: q in i,
    ...                    query_key=str.lower, item_key=str.lower)
    >>> list(finder('GOOGLE'))
    ['www.google.com']

    Note that the `query_matches_item` is sufficient.
    For example, in the above we could have done it like this:

    >>> list(find('GOOGLE', items, lambda q, i: q.lower() in i.lower()))
    ['www.google.com']

    There's never any actual need for the key functions, but they're provided for
    convenience and reuse of general `query_matches_item` functions.

    """
    _query = query_key(query)

    def filt(item):
        return query_matches_item(_query, item_key(item))

    return filter(filt, items)


def _old_find_left_for_educational_purposes(
    strings, query, how="subset", content_func="everywhere"
):
    """
    Example use:

    >>> items = [
    ...     'www.google.com',
    ...     'www.yahoo.com',
    ...     'www.harvard.edu',
    ...     'web.mit.edu',
    ... ]
    >>> _old_find_left_for_educational_purposes(items, 'oo', how='subset')
    ['www.google.com', 'www.yahoo.com']
    >>> _old_find_left_for_educational_purposes(items, 'edu', how='exact')
    []
    >>> _old_find_left_for_educational_purposes(
    ...     items, 'edu', how='exact', content_func='leafs')
    ['www.harvard.edu', 'web.mit.edu']


    """
    if isinstance(content_func, str):
        if content_func == "leafs":
            content_func = lambda x: x.split(".")[-1]
        elif content_func == "everywhere":
            content_func = lambda x: x
        else:
            raise ValueError(
                f"Not a recognised value for content_func argument: {content_func}"
            )

    if how == "exact":
        filt = lambda x: query == content_func(x)
    elif how == "subset":
        filt = lambda x: query in content_func(x)
    else:
        raise ValueError(f"Not a recognised value for how argument: {how}")

    return list(filter(filt, strings))


def extract_encoding_from_contents(content_bytes: bytes):
    r = encoding_spec_re.search(content_bytes)
    if r is not None:
        return r.group(1)
    else:
        return None


def get_encoding(content_bytes: bytes, use_cchardet=DFLT_USE_CCHARDET):
    extracted_encoding = extract_encoding_from_contents(content_bytes)
    if extracted_encoding is not None:
        return extracted_encoding.decode()
    else:
        if use_cchardet:
            r = chardet.detect(content_bytes)
            if r:
                return r["encoding"]
    return None  # if all else fails


decoding_problem_sentinel = "# --- did not manage to decode .py file bytes --- #"


def decode_or_default(
    b: bytes, dflt=decoding_problem_sentinel, use_cchardet=DFLT_USE_CCHARDET
):
    try:
        return b.decode()
    except UnicodeDecodeError:
        encoding = get_encoding(b, use_cchardet=use_cchardet)
        if encoding is not None:
            return b.decode(encoding)
        else:
            return dflt


def resolve_module_filepath(module_spec, assert_output_is_existing_filepath=True) -> str:
    if inspect.ismodule(module_spec):
        module_spec = inspect.getsourcefile(module_spec)
    elif not isinstance(module_spec, str):
        module_spec = inspect.getfile(module_spec)
    if module_spec.endswith("c"):
        module_spec = module_spec[:-1]  # remove the 'c' of '.pyc'
    if os.path.isdir(module_spec):
        module_dir = module_spec
        module_spec = os.path.join(module_dir, "__init__.py")
        assert os.path.isfile(module_spec), (
            f"You specified the module as a directory {module_dir}, "
            f"but this directory wasn't a package (it didn't have an __init__.py file)"
        )
    if assert_output_is_existing_filepath:
        assert os.path.isfile(module_spec), "module_spec should be a file at this point"
    return module_spec


def resolve_to_folder(obj, assert_output_is_existing_folder=True):
    if inspect.ismodule(obj):
        obj = inspect.getsourcefile(obj)
    elif not isinstance(obj, str):
        obj = inspect.getfile(obj)

    if not os.path.isdir(obj):
        if obj.endswith("c"):
            obj = obj[:-1]  # remove the 'c' of '.pyc'
        if obj.endswith("__init__.py"):
            obj = os.path.dirname(obj)
    if assert_output_is_existing_folder:
        assert os.path.isdir(obj), "obj should be a folder at this point"
    return obj


def resolve_module_contents(module_spec, dflt=None, assert_output_is_str=True):
    if not isinstance(module_spec, str) or os.path.isdir(module_spec):
        module_spec = resolve_module_filepath(module_spec)
    if os.path.isfile(module_spec):
        with open(module_spec, "rb") as fp:
            module_bytes = fp.read()
        return decode_or_default(module_bytes, dflt=dflt)
    if assert_output_is_str:
        assert isinstance(
            module_spec, str
        ), f"module_spec should be a string at this point, but was a {type(module_spec)}"
    return module_spec
