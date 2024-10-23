from main.python.options import Options
from main.python.option import Option
from main.python.default_parser import DefaultParser
from main.python.already_selected_exception import AlreadySelectedException
import pytest

class TestDisablePartialMatching:
    
    def test_disable_partial_matching(self):
        parser = DefaultParser(False)
    
        options = Options()
    
        options.add_option(Option("d", "debug", False, "Turn on debug."))
        options.add_option(Option("e", "extract", False, "Turn on extract."))
        options.add_option(Option("o", "option", True, "Turn on option with argument."))
    
        line = parser.parse(options, ["-de", "--option=foobar"])
    
        assert line.has_option("debug"), "There should be an option debug in any case..."
        assert line.has_option("extract"), "There should be an extract option because partial matching is off"
        assert line.has_option("option"), "There should be an option option with a argument value"
    
    
    def test_regular_partial_matching(self):
        parser = DefaultParser()
    
        options = Options()
    
        options.add_option(Option("d", "debug", False, "Turn on debug."))
        options.add_option(Option("e", "extract", False, "Turn on extract."))
        options.add_option(Option("o", "option", True, "Turn on option with argument."))
    
        line = parser.parse(options, ["-de", "--option=foobar"])
        
        assert line.has_option("debug"), "There should be an option debug in any case..."
        assert not line.has_option("extract"), "There should not be an extract option because partial matching only selects debug"
        assert line.has_option("option"), "There should be an option option with a argument value"

