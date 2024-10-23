import pytest
from main.python.option_builder import OptionBuilder
from main.python.options import Options
from main.python.posix_parser import PosixParser

class TestBugCLI13:

    def test_cli13(self):
        debugOpt = "debug"
        debug = OptionBuilder() \
            .with_arg_name(debugOpt) \
            .with_description("turn on debugging") \
            .with_long_opt(debugOpt) \
            .has_arg() \
            .create('d')
        options = Options()
        options.add_option(debug)
        commandLine = PosixParser().parse(options, ["-d", "true"])

        assert "true" == commandLine.get_option_value(debugOpt)
        assert "true" == commandLine.get_option_value('d')
        assert commandLine.has_option('d')
        assert commandLine.has_option(debugOpt)
