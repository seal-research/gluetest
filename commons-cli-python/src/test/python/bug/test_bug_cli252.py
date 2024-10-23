from main.python.parse_exception import ParseException
from main.python.ambiguous_option_exception import AmbiguousOptionException
from main.python.default_parser import DefaultParser
from main.python.option import Option
from main.python.options import Options
import pytest

class TestBugCLI252:
    
    def _get_options(self) -> Options:
        options = Options()
        options.add_option(Option.builder().long_opt("prefix").build())
        options.add_option(Option.builder().long_opt("prefixplusplys").build())
        return options
    
    def test_ambiguous_option_name(self):
        with pytest.raises(AmbiguousOptionException):
            DefaultParser().parse(self._get_options(), ["--pref"])

    def test_exact_option_name_match(self):
        try:
            DefaultParser().parse(self._get_options(), ["--prefix"])
        except ParseException:
            pytest.fail("ParseException raised unexpectedly!")

