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


def decode_or_default(b: bytes, dflt=decoding_problem_sentinel, use_cchardet=DFLT_USE_CCHARDET):
    try:
        return b.decode()
    except UnicodeDecodeError:
        encoding = get_encoding(b, use_cchardet=use_cchardet)
        if encoding is not None:
            return b.decode(encoding)
        else:
            return dflt


def resolve_module_filepath(module_spec):
    if not isinstance(module_spec, str):
        module_spec = inspect.getfile(module_spec)
        if module_spec.endswith('c'):
            module_spec = module_spec[:-1]  # remove the 'c' of '.pyc'
    if os.path.isdir(module_spec):
        module_dir = module_spec
        module_spec = os.path.join(module_dir, '__init__.py')
        assert os.path.isfile(module_spec), \
            f"You specified the module as a directory {module_dir}, " \
            f"but this directory wasn't a package (it didn't have an __init__.py file)"
    assert os.path.isfile(module_spec), "module_spec should be a file at this point"
    return module_spec


def resolve_module_contents(module_spec, dflt=None):
    if not isinstance(module_spec, str) or os.path.isdir(module_spec):
        module_spec = resolve_module_filepath(module_spec)
    if os.path.isfile(module_spec):
        with open(module_spec, 'rb') as fp:
            module_bytes = fp.read()
        return decode_or_default(module_bytes, dflt=dflt)
    assert isinstance(module_spec, str), f"module_spec should be a string at this point, but was a {type(module_spec)}"
    return module_spec
