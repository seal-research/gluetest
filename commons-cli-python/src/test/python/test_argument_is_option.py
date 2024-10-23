import pytest
from main.python.options import Options
from main.python.posix_parser import PosixParser

class TestArgumentIsOption:
     @pytest.fixture(autouse=True)
     def set_up(self):
         self.options = Options().add_option("p", False, "Option p").add_option("attr", True, "Option accepts argument")
         self.parser = PosixParser()


     def test_option(self):
         args = ["-p"]
         cl = self.parser.parse(self.options, args)
         assert cl.has_option("p"), "Confirm -p is set"
         assert not cl.has_option("attr"), "Confirm -attr is not set"
         assert len(cl.get_args()) == 0, "Confirm all arguments recognized"

     def test_option_and_option_with_argument(self):
         args = ["-p", "-attr", "p"]
         cl = self.parser.parse(self.options, args)
         assert cl.has_option("p"), "Confirm -p is set"
         assert cl.has_option("attr"), "Confirm -attr is set"
         assert cl.get_option_value("attr") == "p", "Confirm arg of -attr"
         assert len(cl.get_args()) == 0, "Confirm all arguments recognized"
         
     def test_option_with_argument(self):
         args = ["-attr", "p"]
         cl = self.parser.parse(self.options, args)
         assert not cl.has_option("p"), "Confirm -p is set"
         assert cl.has_option("attr"), "Confirm -attr is set"
         assert cl.get_option_value("attr") == "p", "Confirm arg of -attr"
         assert len(cl.get_args()) == 0, "Confirm all arguments recognized"
