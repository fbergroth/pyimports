from io import BytesIO
from textwrap import dedent

from pyimports import analyze


def _reader(source):
    return BytesIO(dedent(source).encode('utf-8')).readline


def test_extract_names():
    reader = _reader('''
        class Clazz(object):
            pass

        def random():
            return 4  # chosen by fair dice roll

        from .some_module import (SomeClass,  # noqa
                                  some_func)
        import pkg, other_pkg as aspkg
    ''')
    names = analyze.extract_names(reader, include_imports=True)
    assert names == {'Clazz', 'random', 'SomeClass', 'some_func', 'pkg', 'aspkg'}
