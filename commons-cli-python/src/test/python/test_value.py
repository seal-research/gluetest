import pytest
from main.python.options import Options
from main.python.option_builder import OptionBuilder
from main.python.posix_parser import PosixParser

class TestValue:

    def setup_method(self, method):
        self.opts = Options()
        self.opts.add_option("a", False, "toggle -a")
        self.opts.add_option("b", True, "set -b")
        self.opts.add_option("c", "c", False, "toggle -c")
        self.opts.add_option("d", "d", True, "set -d")

        self.opts.add_option(OptionBuilder().has_optional_arg().create('e'))
        self.opts.add_option(OptionBuilder().has_optional_arg().with_long_opt("fish").create())
        self.opts.add_option(OptionBuilder().has_optional_args().with_long_opt("gravy").create())
        self.opts.add_option(OptionBuilder().has_optional_args(2).with_long_opt("hide").create())
        self.opts.add_option(OptionBuilder().has_optional_args(2).create('i'))
        self.opts.add_option(OptionBuilder().has_optional_args().create('j'))

        args = ["-a", "-b", "foo", "--c", "--d", "bar"]

        self.parser = PosixParser()
        self.cl = self.parser.parse(self.opts, args)

    def test_long_no_arg(self):
        assert self.cl.has_option("c")
        assert self.cl.get_option_value("c") is None

    def test_long_no_arg_with_option(self):
        assert self.cl.has_option(self.opts.get_option("c"))
        assert self.cl.get_option_value(self.opts.get_option("c")) is None

    def test_long_optional_arg_value(self):
        args = ["--fish", "face"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("fish")
        assert cmd.get_option_value("fish") == "face"

    def test_long_optional_arg_values(self):
        args = ["--gravy", "gold", "garden"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("gravy")
        assert cmd.get_option_value("gravy") == "gold"
        assert cmd.get_option_values("gravy")[0] == "gold"
        assert cmd.get_option_values("gravy")[1] == "garden"
        assert len(cmd.args) == 0

    def test_long_optional_arg_values_with_option(self):
        args = ["--gravy", "gold", "garden"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)

        assert cmd.has_option(self.opts.get_option("gravy"))
        assert cmd.get_option_value(self.opts.get_option("gravy")) == "gold"
        assert cmd.get_option_values(self.opts.get_option("gravy"))[0] == "gold"
        assert cmd.get_option_values(self.opts.get_option("gravy"))[1] == "garden"
        assert len(cmd.args) == 0

    def test_long_optional_arg_value_with_option(self):
        args = ["--fish", "face"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option(self.opts.get_option("fish"))
        assert cmd.get_option_value(self.opts.get_option("fish")) == "face"
        
    def test_long_optional_n_arg_values(self):
        args = ["--hide", "house", "hair", "head"]

        parser = PosixParser()

        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("hide")
        assert cmd.get_option_value("hide") == "house"
        assert cmd.get_option_values("hide")[0] == "house"
        assert cmd.get_option_values("hide")[1] == "hair"
        assert len(cmd.args) == 1
        assert cmd.args[0] == "head"

    def test_long_optional_n_arg_values_with_option(self):
        args = ["--hide", "house", "hair", "head"]

        parser = PosixParser()

        cmd = parser.parse(self.opts, args)
        assert cmd.has_option(self.opts.get_option("hide"))
        assert cmd.get_option_value(self.opts.get_option("hide")) == "house"
        assert cmd.get_option_values(self.opts.get_option("hide"))[0] == "house"
        assert cmd.get_option_values(self.opts.get_option("hide"))[1] == "hair"
        assert len(cmd.args) == 1
        assert cmd.args[0] == "head"

    def test_long_optional_no_value(self):
        args = ["--fish"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("fish")
        assert cmd.get_option_value("fish") is None

    def test_long_optional_no_value_with_option(self):
        args = ["--fish"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option(self.opts.get_option("fish"))
        assert cmd.get_option_value(self.opts.get_option("fish")) is None
    
    def test_long_with_arg(self):
        assert self.cl.has_option("d")
        assert self.cl.get_option_value("d") is not None
        assert self.cl.get_option_value("d") == "bar"

    def test_long_with_arg_with_option(self):
        assert self.cl.has_option(self.opts.get_option("d"))
        assert self.cl.get_option_value(self.opts.get_option("d")) is not None
        assert self.cl.get_option_value(self.opts.get_option("d")) == "bar"
    
    def test_short_no_arg(self):
        assert self.cl.has_option("a")
        assert self.cl.get_option_value("a") is None

    def test_short_no_arg_with_option(self):
        assert self.cl.has_option(self.opts.get_option("a"))
        assert self.cl.get_option_value(self.opts.get_option("a")) is None

    def test_short_optional_arg_no_value(self):
        args = ["-e"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("e")
        assert cmd.get_option_value("e") is None

    def test_short_optional_arg_no_value_with_option(self):
        args = ["-e"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option(self.opts.get_option("e"))
        assert cmd.get_option_value(self.opts.get_option("e")) is None

    def test_short_optional_arg_value(self):    
        args = ["-e", "everything"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("e")
        assert cmd.get_option_value("e") == "everything"

    def test_short_optional_arg_values(self):
        args = ["-j", "ink", "idea"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("j")
        assert cmd.get_option_value("j") == "ink"
        assert cmd.get_option_values("j")[0] == "ink"
        assert cmd.get_option_values("j")[1] == "idea"
        assert len(cmd.args) == 0

    def test_short_optional_arg_values_with_option(self):
        args = ["-j", "ink", "idea"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option(self.opts.get_option("j"))
        assert cmd.get_option_value(self.opts.get_option("j")) == "ink"
        assert cmd.get_option_values(self.opts.get_option("j"))[0] == "ink"
        assert cmd.get_option_values(self.opts.get_option("j"))[1] == "idea"
        assert len(cmd.args) == 0

    def test_short_optional_arg_value_with_option(self):
        args = ["-e", "everything"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option(self.opts.get_option("e"))
        assert cmd.get_option_value(self.opts.get_option("e")) == "everything"

    def test_short_optional_n_arg_values(self):
        args = ["-i", "ink", "idea", "isotope", "ice"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("i")
        assert cmd.get_option_value("i") == "ink"
        assert cmd.get_option_values("i")[0] == "ink"
        assert cmd.get_option_values("i")[1] == "idea"
        assert len(cmd.args) == 2
        assert cmd.args[0] == "isotope"
        assert cmd.args[1] == "ice"

    def test_short_optional_n_arg_values_with_option(self):
        args = ["-i", "ink", "idea", "isotope", "ice"]

        parser = PosixParser()
        cmd = parser.parse(self.opts, args)
        assert cmd.has_option("i")
        assert cmd.get_option_value(self.opts.get_option("i")) == "ink"
        assert cmd.get_option_values(self.opts.get_option("i"))[0] == "ink"
        assert cmd.get_option_values(self.opts.get_option("i"))[1] == "idea"
        assert len(cmd.args) == 2
        assert cmd.args[0] == "isotope"
        assert cmd.args[1] == "ice"

    def test_short_with_arg(self):
        assert self.cl.has_option("b")
        assert self.cl.get_option_value("b") is not None
        assert self.cl.get_option_value("b") == "foo"

    def test_short_with_arg_with_option(self):
        assert self.cl.has_option(self.opts.get_option("b"))
        assert self.cl.get_option_value(self.opts.get_option("b")) is not None
        assert self.cl.get_option_value(self.opts.get_option("b")) == "foo"
