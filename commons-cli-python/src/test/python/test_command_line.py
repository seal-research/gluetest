from main.python.options import Options
from main.python.option import Option
from main.python.gnu_parser import GnuParser
from main.python.command_line import CommandLine
from main.python.option_builder import OptionBuilder
from main.python.default_parser import DefaultParser
import pytest

class TestCommandLine:
    def test_builder(self):
        builder = CommandLine.Builder()
        builder.add_arg("foo").add_arg("bar")
        builder.add_option(Option.builder("T").build())
        cmd = builder.build()

        assert cmd.get_args()[0] == "foo"
        assert cmd.get_arg_list()[1] == "bar"
        assert cmd.get_options()[0].get_opt() == "T"
        
    def test_get_option_properties(self):
        args = ["-Dparam1=value1", "-Dparam2=value2", "-Dparam3", "-Dparam4=value4", "-D", "--property", "foo=bar"]

        options = Options()
        options.add_option(OptionBuilder().with_value_separator().has_optional_args(2).create('D'))
        options.add_option(OptionBuilder().with_value_separator().has_args(2).with_long_opt("property").create())

        parser = GnuParser()
        cl = parser.parse(options, args)

        props = cl.get_option_properties("D")
        assert props is not None
        assert len(props) == 4
        assert props["param1"] == "value1"
        assert props["param2"] == "value2"
        assert props["param3"] == "true"
        assert props["param4"] == "value4"

        assert cl.get_option_properties("property")["foo"] == "bar"

    def test_get_option_properties_with_option(self):
        args = ["-Dparam1=value1", "-Dparam2=value2", "-Dparam3", "-Dparam4=value4", "-D", "--property", "foo=bar"]

        options = Options()
        optionD = OptionBuilder().with_value_separator().has_optional_args(2).create('D')
        optionProperty = OptionBuilder().with_value_separator().has_args(2).with_long_opt("property").create()
        options.add_option(optionD)
        options.add_option(optionProperty)

        parser = GnuParser()
        cl = parser.parse(options, args)

        props = cl.get_option_properties(optionD)
        assert props is not None
        assert len(props) == 4
        assert props["param1"] == "value1"
        assert props["param2"] == "value2"
        assert props["param3"] == "true"
        assert props["param4"] == "value4"

        assert cl.get_option_properties(optionProperty)["foo"] == "bar"

    def test_get_options(self):
        cmd = CommandLine()
        assert cmd.get_options() is not None
        assert len(cmd.get_options()) == 0

        cmd.add_option(Option("a", None))
        cmd.add_option(Option("b", None))
        cmd.add_option(Option("c", None))

        assert len(cmd.get_options()) == 3

    def test_get_parsed_option_value(self):
        options = Options()
        options.add_option(OptionBuilder().has_arg().with_type(int).create("i"))
        options.add_option(OptionBuilder().has_arg().create("f"))

        parser = DefaultParser()
        cmd = parser.parse(options, ["-i", "123", "-f", "foo"])

        assert int(cmd.get_parsed_option_value("i")) == 123
        assert cmd.get_parsed_option_value("f") == "foo"

    def test_get_parsed_option_value_with_char(self):
        options = Options()
        options.add_option(Option.builder("i").has_arg().type(int).build())
        options.add_option(Option.builder("f").has_arg().build())

        parser = DefaultParser()
        cmd = parser.parse(options, ["-i", "123", "-f", "foo"])

        assert int(cmd.get_parsed_option_value('i')) == 123
        assert cmd.get_parsed_option_value('f') == "foo"

    def test_get_parsed_option_value_with_option(self):
        options = Options()
        optI = Option.builder("i").has_arg().type(int).build()
        optF = Option.builder("f").has_arg().build()
        options.add_option(optI)
        options.add_option(optF)

        parser = DefaultParser()
        cmd = parser.parse(options, ["-i", "123", "-f", "foo"])

        assert cmd.get_parsed_option_value(optI) == 123
        assert cmd.get_parsed_option_value(optF) == "foo"

    def test_null_option(self):
        options = Options()
        optI = Option.builder("i").has_arg().type(int).build()
        optF = Option.builder("f").has_arg().build()
        options.add_option(optI)
        options.add_option(optF)
        parser = DefaultParser()
        cmd = parser.parse(options, ["-i", "123", "-f", "foo"])
        assert cmd.get_option_value(None) is None
        assert cmd.get_parsed_option_value(None) is None
