import pytest
from main.python.util import Util

def test_strip_leading_and_trailing_quotes():
    assert Util.strip_leading_and_trailing_quotes('"foo"') == 'foo'
    assert Util.strip_leading_and_trailing_quotes('foo "bar"') == 'foo "bar"'
    assert Util.strip_leading_and_trailing_quotes('"foo" bar') == '"foo" bar'
    assert Util.strip_leading_and_trailing_quotes('"foo" and "bar"') == '"foo" and "bar"'
    assert Util.strip_leading_and_trailing_quotes('"') == '"'

def test_strip_leading_hyphens():
    assert Util.strip_leading_hyphens('-f') == 'f'
    assert Util.strip_leading_hyphens('--foo') == 'foo'
    assert Util.strip_leading_hyphens('---foo') == '-foo'
    assert Util.strip_leading_hyphens(None) is None
