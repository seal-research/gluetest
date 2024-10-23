import pytest
from main.python.option import Option
from main.python.options import Options
from main.python.posix_parser import PosixParser
from main.python.missing_argument_exception import MissingArgumentException

class TestBugCLI71:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.options = Options()
        
        algorithm = Option("a", "algo", True, "the algorithm which it to perform executing")
        algorithm.set_arg_name("algorithm name")
        self.options.add_option(algorithm)

        key = Option("k", "key", True, "the key the setted algorithm uses to process")
        algorithm.set_arg_name("value")
        self.options.add_option(key)

        self.parser = PosixParser()

    def test_basic(self):
        args = ["-a", "Caesar", "-k", "A"]
        line = self.parser.parse(self.options, args)
        assert line.get_option_value("a") == "Caesar"
        assert line.get_option_value("k") == "A"

    def test_gets_default_if_optional(self):
        args = ["-k", "-a", "Caesar"]
        self.options.get_option("k").set_optional_arg(True)
        line = self.parser.parse(self.options, args)

        assert line.get_option_value("a") == "Caesar"
        assert line.get_option_value('k', "a") == "a"
    
    def test_lack_of_error(self):
        args = ["-k", "-a", "Caesar"]
        try:
            self.parser.parse(self.options, args)
            pytest.fail("MissingArgumentException expected")
        except MissingArgumentException as e:
            assert e.get_option().get_opt() == "k", "option missing an argument"

    def test_mistaken_argument(self):
        args = ["-a", "Caesar", "-k", "A"]
        line = self.parser.parse(self.options, args)
        args = ["-a", "Caesar", "-k", "a"]
        line = self.parser.parse(self.options, args)
        assert line.get_option_value("a") == "Caesar"
        assert line.get_option_value("k") == "a"
