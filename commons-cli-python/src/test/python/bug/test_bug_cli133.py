import pytest
from main.python.option import Option
from main.python.options import Options
from main.python.posix_parser import PosixParser

class TestBugCLI133:

    def test_order(self):
        optionA = Option("a", "first")
        opts = Options()
        opts.add_option(optionA)
        posix_parser = PosixParser()
        line = posix_parser.parse(opts, None)
        assert not line.has_option(str(None))
