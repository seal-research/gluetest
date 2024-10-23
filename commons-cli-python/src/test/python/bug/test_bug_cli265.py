from main.python.options import Options
from main.python.option import Option
from main.python.default_parser import DefaultParser
import pytest

class TestBugCLI265:
    """
    Test for CLI-265
    The issue is that a short option with an optional value will use whatever comes next as value.
    """
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.parser = DefaultParser()
        
        option_t1 = Option.builder("t1").has_arg().number_of_args(1).optional_arg(True).arg_name("t1_path").build()
        option_a = Option.builder("a").has_arg(False).build()
        option_b = Option.builder("b").has_arg(False).build()
        option_last = Option.builder("last").has_arg(False).build()
        
        self.options = Options().add_option(option_t1).add_option(option_a).add_option(option_b).add_option(option_last)
    
    def test_should_parse_concatenated_short_options(self):
        concatenated_short_options = ["-t1", "-ab"]

        command_line = self.parser.parse(self.options, concatenated_short_options)

        assert command_line.has_option("t1")
        assert command_line.get_option_value("t1") == None
        assert command_line.has_option("a")
        assert command_line.has_option("b")
        assert not command_line.has_option("last")
    
    def test_should_parse_short_option_without_value(self):
        two_short_options = ["-t1", "-last"]
        
        command_line = self.parser.parse(self.options, two_short_options)

        assert command_line.has_option("t1")
        assert "-last" != command_line.get_option_value("t1"), "Second option has been used as value for first option"
        assert command_line.has_option("last"), "Second option has not been detected"
    
    def test_should_parse_short_option_with_value(self):
        short_option_with_value = ["-t1", "path/to/my/db"]

        command_line = self.parser.parse(self.options, short_option_with_value)

        assert "path/to/my/db" == command_line.get_option_value("t1")
        assert not command_line.has_option("last")
