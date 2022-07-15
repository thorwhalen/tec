"""Builtin tec utils"""

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

encoding_spec_re = re.compile(b'-*- coding: (.+) -*-')


import operator
from typing import Any, Callable, Iterable

Query = Any
Item = Any


def identity(x):
    return x


def find(
    query: Any,
    items: Iterable[Item],
    query_matches_item: Callable[[Query, Item], bool] = operator.eq,
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
    strings, query, how='subset', content_func='everywhere'
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
        if content_func == 'leafs':
            content_func = lambda x: x.split('.')[-1]
        elif content_func == 'everywhere':
            content_func = lambda x: x
        else:
            raise ValueError(
                f'Not a recognised value for content_func argument: {content_func}'
            )

    if how == 'exact':
        filt = lambda x: query == content_func(x)
    elif how == 'subset':
        filt = lambda x: query in content_func(x)
    else:
        raise ValueError(f'Not a recognised value for how argument: {how}')

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
                return r['encoding']
    return None  # if all else fails


decoding_problem_sentinel = '# --- did not manage to decode .py file bytes --- #'


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


# Pattern: meshed
def resolve_module_filepath(
    module_spec, assert_output_is_existing_filepath=True
) -> str:
    if inspect.ismodule(module_spec):
        module_spec = inspect.getsourcefile(module_spec)
    elif not isinstance(module_spec, str):
        module_spec = inspect.getfile(module_spec)
    if module_spec.endswith('c'):
        module_spec = module_spec[:-1]  # remove the 'c' of '.pyc'
    if os.path.isdir(module_spec):
        module_dir = module_spec
        module_spec = os.path.join(module_dir, '__init__.py')
        assert os.path.isfile(module_spec), (
            f'You specified the module as a directory {module_dir}, '
            f"but this directory wasn't a package (it didn't have an __init__.py file)"
        )
    if assert_output_is_existing_filepath:
        assert os.path.isfile(module_spec), 'module_spec should be a file at this point'
    return module_spec


# Pattern: meshed
def resolve_to_folder(obj, assert_output_is_existing_folder=True):
    if inspect.ismodule(obj):
        obj = inspect.getsourcefile(obj)
    elif not isinstance(obj, str):
        obj = inspect.getfile(obj)

    if not os.path.isdir(obj):
        if obj.endswith('c'):
            obj = obj[:-1]  # remove the 'c' of '.pyc'
        if obj.endswith('__init__.py'):
            obj = os.path.dirname(obj)
    if assert_output_is_existing_folder:
        assert os.path.isdir(obj), 'obj should be a folder at this point'
    return obj


# Pattern: meshed
def resolve_module_contents(module_spec, dflt=None, assert_output_is_str=True):
    if not isinstance(module_spec, str) or os.path.isdir(module_spec):
        module_spec = resolve_module_filepath(module_spec)
    if os.path.isfile(module_spec):
        with open(module_spec, 'rb') as fp:
            module_bytes = fp.read()
        return decode_or_default(module_bytes, dflt=dflt)
    if assert_output_is_str:
        assert isinstance(
            module_spec, str
        ), f'module_spec should be a string at this point, but was a {type(module_spec)}'
    return module_spec


# ---------------------------------------------------------------------------------------
# TODO: Compare and merge
# What's below was developed independently but has strong ties with what's above, so
# should probably be merged, or at least synched to reduce unnecessary entropy

from contextlib import suppress
from operator import attrgetter, methodcaller
from functools import partial
from importlib import import_module
from typing import Optional, Callable, Iterable, Any, Sequence, Mapping, Sized
import re
from inspect import signature

module_not_found_ignore = suppress(ModuleNotFoundError, ImportError)

not_found_sentinel = object()


def import_and_add_if_available(
    obj_name: str,
    module_name: str,
    as_name: Optional[str] = None,
    scope: dict = None,
    if_already_in_scope: Optional[Callable] = None,
    if_not_found: Optional[Callable] = None,
):
    """
    Import object named ``obj_name`` from module named ``module_name``, sticking it
    in scope (a dict, usually locals()).

    :param scope: A dict where the object will be stored (if found). Usually locals().
    :param obj_name: The name of the object to import
    :param module_name: The name of the module to import the object from
    :param as_name: The name to use in the scope. Defaults to ``obj_name``
    :param if_already_in_scope: If not None, should be a ``(scope, as_name, obj)``
        callable that will provide the return value if ``as_name`` is already in the
        scope.
        This is to be able to overwrite the default of simply doing a
        ``scope[as_name] = obj`` (having the net effect of resolving name conflicts
        by a "last one seen wins" strategy.
    :param if_not_found: If not None, should be a ``(obj_name, module_name)`` callable
        that will provide the return value if ``obj_name`` is not found in
        ``module_name``.

    :return:

    >>> from qo.qo_utils import import_and_add_if_available
    >>> from functools import partial  # not necessary, but represents use case
    >>> scope = dict()  # you'd usually put locals() here
    >>> acquire = partial(import_and_add_if_available, scope=scope)
    >>> acquire('join', 'os.path')
    True
    >>> acquire('isfile', 'os.path', as_name='check_if_file_exists')
    True
    >>> acquire('not_in_os_path', 'os.path')  # returns False: not found in os.path
    False
    >>> acquire('object', 'does.not.exist')  # returns None: the module_name not found
    >>> import os
    >>> assert (scope ==
    ...     {'join': os.path.join, 'check_if_file_exists': os.path.isfile}
    ... )

    See in the above that neither ``'not_in_os_path'`` nor ``'object'`` are in
    ``scope``. They were simply skipped.

    """
    as_name = as_name or obj_name
    assert scope is not None, 'You need to specify a scope. Usually, scope=locals()'
    with module_not_found_ignore:
        module_obj = import_module(module_name)
        obj = getattr(module_obj, obj_name, not_found_sentinel)
        if obj is not not_found_sentinel:
            if if_already_in_scope and as_name in scope:
                return if_already_in_scope(scope, as_name, obj)
            else:
                scope[as_name] = obj
                return True
        else:
            if if_not_found is None:
                return False
            else:
                return if_not_found(obj_name, module_name)
    return None
    # returns None if module couldn't be imported!


# ---------------------------------------------------------------------------------------
ddir = lambda o: filter(lambda x: not x.startswith('_'), dir(o))

StringIterableFactory = Callable[[Any], Iterable[str]]
ObjectToString = Callable[[Any], str]

_if_not_iterable_get_attributes: StringIterableFactory


def _if_not_iterable_get_attributes(x: Any) -> Iterable[str]:
    if not isinstance(x, Iterable):
        x = list(ddir(x))
    return x


def _attribute_name_object_pairs(obj: Any):
    for attr_name in ddir(obj):
        yield attr_name, getattr(obj, attr_name)


def _not_prefixed_by_underscore(x: str) -> bool:
    return not x.startswith('_')


def _is_pair(x):
    return isinstance(x, Iterable) and isinstance(x, Sized) and len(x) == 2


# Pattern: meshed
def name_and_object_pairs(
    objects: Any,
    objects_to_iterable: Callable[..., Iterable] = _attribute_name_object_pairs,
    *,
    name_filt: Callable[..., bool] = _not_prefixed_by_underscore,
    obj_filt: Callable[..., bool] = callable,
    name_of_obj: ObjectToString = attrgetter('__name__'),
):
    """Get (name, object) pairs from source of objects

    :param objects: The source we want to extract name and object pairs from.
        Could be an explicit list of pairs, or a single object (like a module)
        from which we'll generate these (using ``objects_to_iterable``)
    :param objects_to_iterable: If the input ``objects`` isn't already an iterable,
        the function to make it so
    :param name_filt: A condition on the name
    :param obj_filt: A condition on the object
    :param name_of_obj: when an element of the iterable isn't a (name, obj) pair,
        the function to get the name of a the object.

    Get method names of the dict class:

    >>> next(zip(*name_and_object_pairs(dict)))

    Get only those names of dict methods that contain the string 'keys':

    >>> next(zip(*name_and_object_pairs(dict, name_filt=lambda x: 'keys' in x)))

    """
    if not isinstance(objects, Iterable):
        objects = objects_to_iterable(objects)

    let_everything_through_filter = lambda x: True
    name_filt = name_filt or let_everything_through_filter
    obj_filt = obj_filt or let_everything_through_filter

    def filt(pair):
        obj_name, obj = pair
        return name_filt(obj_name) and obj_filt(obj)

    def ensure_pair(pair):
        if _is_pair(pair):
            # unpack pair (assuming it's a (name, obj) pair already)
            return pair  # assume it's a (name, obj) pair already
        else:
            obj = pair
            return name_of_obj(obj), obj

    if isinstance(objects, Mapping):
        yield from filter(filt, objects.items())
    else:
        yield from filter(filt, map(ensure_pair, objects))


def signature_strings(objects, object_to_strings: StringIterableFactory = ddir):
    """A generator of strings describing the callables in obj (module, class, ...)"""
    for name, obj in name_and_object_pairs(objects):
        if callable(obj):
            yield f'{name}{signature(obj)}'


def print_signatures(obj, object_to_strings: StringIterableFactory = ddir, sep='\n * '):
    """Prints information on callable attributes of obj (module, class, ...)"""
    print('', *signature_strings(obj, object_to_strings), sep=sep)


def find_objects(
    pattern: str,
    objects: Any,
    objects_to_strings: StringIterableFactory = _if_not_iterable_get_attributes,
    *,
    key=None,
):
    """Find strings matching a given pattern, possibly sorting them in a specific way.

    :param pattern: The pattern to search (string representing a regular expression).
    :param objects: An iterable of strings or an object that will resolve in one.
    :param objects_to_strings: The function that resolves the ``objects`` input
        (which is not even necessarily an iterable) into an iterable of strings.
    :param key: If not None, will be used to sort matched objects.
        ``key`` will be applied to objects of type ``re.Match``;
        see https://docs.python.org/3/library/re.html#match-objects to get an idea of
        how to define the right key function.
        If ``key`` is an iterable ("of callables", assumed), make an
        aggregate of these functions that will return a tuple of the sort keys.
        This is akin to sorting by one columns primarly, a second secondarily, etc.
    :return: A generator of matched strings.

    >>> kwargs = dict(
    ...     pattern='li',
    ...     objects='bob and lilabet like to play with alice',
    ...     objects_to_strings=str.split,
    ... )
    >>> list(find_objects(**kwargs))
    ['lilabet', 'like', 'alice']

    Sort the results in reverse length of string:

    >>> list(find_objects(**kwargs, key=lambda x: -len(x.string)))
    ['lilabet', 'alice', 'like']

    Sort the results according to how early in the string the match happens:

    >>> from operator import methodcaller
    >>> list(find_objects(**kwargs, key=methodcaller('span')))
    ['lilabet', 'like', 'alice']

    The same as above, but with secondary "length" sorting:

    >>> tuple(  # for a change!
    ...     find_objects(**kwargs, key=[methodcaller('span'), lambda x: len(x.string)])
    ... )
    ('like', 'lilabet', 'alice')
    """
    strings = list(objects_to_strings(objects))
    pattern = re.compile(pattern)
    match_objects = list(map(pattern.search, strings))

    # The match_objects are re.Match instances that resolve to True when there's a match,
    # and can therefore be used as selectors
    match_objects = list(bitmap_selection(match_objects, selector=match_objects))

    if key is not None:
        if isinstance(key, Iterable):
            # If match_sort_key is an iterable ("of callables", assumed), make an
            # aggregate of these functions that will return a tuple of the sort keys.
            # This is akin to sorting by one columns primarly, a second secondarily, etc.
            _key = partial(func_fanout, funcs=key)
            key = lambda x: tuple(_key(x))
        match_objects = sorted(match_objects, key=key)

    # instead of getting the strings from strings, we get them from the re.Match objects'
    # 'string' attribute, because these contain more information to be able to sort with
    return map(attrgetter('string'), match_objects)


def func_fanout(*args, funcs: Iterable[Callable], **kwargs):
    """Util to make a function that applies multiple functions to a single input.
    Note that the function returns a generator that needs to be "consumed" to actually
    get the outputs of the function.

    ``func_fanout`` is meant to be used with ``functools.partial`` to "make" the
    desired function, such as:

    >>> from functools import partial
    >>> f = partial(func_fanout, funcs=[
    ...     lambda x, y: x + y,
    ...     lambda x, y: x * y,
    ... ])
    >>> list(f(2, 3))
    [5, 6]
    >>> tuple(f(3, y=4))
    (7, 12)

    .. seealso: ``i2.multi_object.FuncFanout`` for a more involved version of this.

    """
    return (func(*args, **kwargs) for func in funcs)


def bitmap_selection(iterable: Iterable, selector: Sequence):
    """Select items of an iterable with items of a selector sequence of the same size.
    The selector items should be, or resolve to, a ``bool``.

    >>> list(bitmap_selection([2, 4, 6, 8], [True, False, True, False]))
    [2, 6]
    >>> tuple(bitmap_selection(range(5), [1, 0, None, '', 'blah']))
    (0, 4)

    """
    return (obj for i, obj in enumerate(iterable) if selector[i])
