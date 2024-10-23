import pytest
from main.python.options import Options
from main.python.option_builder import OptionBuilder
from main.python.posix_parser import PosixParser

class TestValues:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.opts = Options()
        self.opts.add_option("a", False, "toggle -a")
        self.opts.add_option("b", True, "set -b")
        self.opts.add_option("c", "c", False, "toggle -c")
        self.opts.add_option("d", "d", True, "set -d")

        self.opts.add_option(OptionBuilder().with_long_opt("e").has_args().with_description("set -e ").create('e'))
        self.opts.add_option("f", "f", False, "jk")
        self.opts.add_option(OptionBuilder().with_long_opt("g").has_args(2).with_description("set -g").create('g'))
        self.opts.add_option(OptionBuilder().with_long_opt("h").has_arg().with_description("set -h").create('h'))
        self.opts.add_option(OptionBuilder().with_long_opt("i").with_description("set -i").create('i'))
        self.opts.add_option(OptionBuilder().with_long_opt("j").has_args().with_description("set -j").with_value_separator('=').create('j'))
        self.opts.add_option(OptionBuilder().with_long_opt("k").has_args().with_description("set -k").with_value_separator('=').create('k'))
        self.opts.add_option(OptionBuilder().with_long_opt("m").has_args().with_description("set -m").with_value_separator().create('m'))

        args = [
            "-a",
            "-b", "foo",
            "--c",
            "--d", "bar",
            "-e", "one", "two",
            "-f",
            "arg1", "arg2",
            "-g", "val1", "val2", "arg3",
            "-h", "val1", "-i",
            "-h", "val2",
            "-jkey=value",
            "-j", "key=value",
            "-kkey1=value1",
            "-kkey2=value2",
            "-mkey=value"
        ]

        parser = PosixParser()
        self.cmd = parser.parse(self.opts, args)

    def test_char_separator(self):
        # tests the char methods of CommandLine that delegate to the String methods
        assert self.cmd.has_option("j"), "Option j is not set"
        assert self.cmd.has_option('j'), "Option j is not set"
        assert self.cmd.get_option_values("j") == ["key", "value", "key", "value"]
        assert self.cmd.get_option_values('j') == ["key", "value", "key", "value"]

        assert self.cmd.has_option("k"), "Option k is not set"
        assert self.cmd.has_option('k'), "Option k is not set"
        assert self.cmd.get_option_values("k") == ["key1", "value1", "key2", "value2"]
        assert self.cmd.get_option_values('k') == ["key1", "value1", "key2", "value2"]

        assert self.cmd.has_option("m"), "Option m is not set"
        assert self.cmd.has_option('m'), "Option m is not set"
        assert self.cmd.get_option_values("m") == ["key", "value"]
        assert self.cmd.get_option_values('m') == ["key", "value"]

    def test_complex_values(self):
        assert self.cmd.has_option("i"), "Option i is not set"
        assert self.cmd.has_option("h"), "Option h is not set"
        assert self.cmd.get_option_values("h") == ["val1", "val2"]
    
    def test_extra_args(self):
        assert self.cmd.get_args() == ["arg1", "arg2", "arg3"], "Extra args"

    def test_multiple_arg_values(self):
        assert self.cmd.has_option("e"), "Option e is not set"
        assert self.cmd.get_option_values("e") == ["one", "two"]

    def test_short_args(self):
        assert self.cmd.has_option("a"), "Option a is not set"
        assert self.cmd.has_option("c"), "Option c is not set"

        assert self.cmd.get_option_values("a") == None
        assert self.cmd.get_option_values("c") == None

    def test_short_args_with_value(self):
        assert self.cmd.has_option("b"), "Option b is not set"
        assert self.cmd.get_option_value("b") == "foo"
        assert len(self.cmd.get_option_values("b")) == 1

        assert self.cmd.has_option("d"), "Option d is not set"
        assert self.cmd.get_option_value("d") == "bar"
        assert len(self.cmd.get_option_values("d")) == 1
    
    def test_two_arg_values(self):
        assert self.cmd.has_option("g"), "Option g is not set"
        assert self.cmd.get_option_values("g") == ["val1", "val2"]
    
    # 
    # test_get_value was not translated
    # 
