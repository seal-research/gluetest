import pytest
from main.python.options import Options
from main.python.option_builder import OptionBuilder
from main.python.posix_parser import PosixParser

class TestBugCLI148:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.options = Options()
        self.options.add_option(OptionBuilder.has_arg().create('t'))
        self.options.add_option(OptionBuilder.has_arg().create('s'))

    def test_workaround1(self):
        parser = PosixParser()
        args = ["-t-something"]

        command_line = parser.parse(self.options, args)
        assert command_line.get_option_value('t') == "-something"

    def test_workaround2(self):
        parser = PosixParser()
        args = ["-t", "\"-something\""]

        command_line = parser.parse(self.options, args)
        assert command_line.get_option_value('t') == "-something"
