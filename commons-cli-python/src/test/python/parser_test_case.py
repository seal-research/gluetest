import pytest
from main.python.options import Options
from main.python.option_group import OptionGroup
from main.python.parser import Parser
from main.python.default_parser import DefaultParser
from main.python.option_builder import OptionBuilder
from main.python.ambiguous_option_exception import AmbiguousOptionException
from main.python.missing_argument_exception import MissingArgumentException
from main.python.unrecognized_option_exception import UnrecognizedOptionException
from main.python.missing_option_exception import MissingOptionException
from main.python.parse_exception import ParseException

class ParserTestCase:
    """
    Abstract test case testing common parser features.
    """
        
    def parse(self, parser, opts: Options, args: list[str], properties: dict):
        if isinstance(parser, Parser):
            return parser.parse(opts, args, properties)
        if isinstance(parser, DefaultParser):
            return parser.parse(opts, args, properties)
        raise AttributeError("Default options not supported by this parser")

    @pytest.fixture(autouse=True)
    def set_up(self):
        self._self_up()

    def _set_up(self):
        self.parser = Parser()

        self.options = Options() \
            .add_option("a", "enable-a", False, "turn [a] on or off") \
            .add_option("b", "bfile", True, "set the value of [b]") \
            .add_option("c", "copt", False, "turn [c] on or off")

    def test_ambiguous_long_without_equal_single_dash(self):
        args = ["-b", "-foobar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_optional_arg().create('f'))
        options.add_option(OptionBuilder.with_long_opt("bar").has_optional_arg().create('b'))

        cl = self.parser.parse(options, args)

        assert cl.has_option("b")
        assert cl.has_option("f")
        assert cl.get_option_value("foo") == "bar"

    def test_ambiguous_partial_long_option1(self):
        args = ["--ver"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("verbose").create())

        caught = False

        try:
            self.parser.parse(options, args)
        except AmbiguousOptionException as e:
            caught = True
            assert e.get_option() == "--ver", "Partial option"
            assert e.get_matching_options() is not None, "Matching options null"
            assert len(e.get_matching_options()) == 2, "Matching options size"

        assert caught, "Confirm MissingArgumentException caught"

    def test_ambiguous_partial_long_option2(self):
        args = ["-ver"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("verbose").create())

        caught = False

        try:
            self.parser.parse(options, args)
        except AmbiguousOptionException as e:
            caught = True
            assert e.get_option() == "-ver", "Partial option"
            assert e.get_matching_options() is not None, "Matching options null"
            assert len(e.get_matching_options()) == 2, "Matching options size"

        assert caught, "Confirm MissingArgumentException caught"

    def test_ambiguous_partial_long_option3(self):
        args = ["--ver=1"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("verbose").has_optional_arg().create())

        caught = False

        try:
            self.parser.parse(options, args)
        except AmbiguousOptionException as e:
            caught = True
            assert e.get_option() == "--ver", "Partial option"
            assert e.get_matching_options() is not None, "Matching options null"
            assert len(e.get_matching_options()) == 2, "Matching options size"

        assert caught, "Confirm MissingArgumentException caught"

    def test_ambiguous_partial_long_option4(self):
        args = ["-ver=1"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("verbose").has_optional_arg().create())

        caught = False

        try:
            self.parser.parse(options, args)
        except AmbiguousOptionException as e:
            caught = True
            assert e.get_option() == "-ver", "Partial option"
            assert e.get_matching_options() is not None, "Matching options null"
            assert len(e.get_matching_options()) == 2, "Matching options size"

        assert caught, "Confirm MissingArgumentException caught"

    def test_argument_starting_with_hyphen(self):
        args = ["-b", "-foo"]

        cl = self.parser.parse(self.options, args)
        assert cl.get_option_value("b") == "-foo"

    def test_bursting(self):
        args = ["-acbtoast", "foo", "bar"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("a"), "Confirm -a is set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.has_option("c"), "Confirm -c is set"
        assert cl.get_option_value("b") == "toast", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 2, "Confirm size of extra args"

    def test_double_dash1(self):
        args = ["--copt", "--", "-b", "toast"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("c"), "Confirm -c is set"
        assert not cl.has_option("b"), "Confirm -b is not set"
        assert len(cl.get_arg_list()) == 2, "Confirm 2 extra args: " + str(len(cl.get_arg_list()))

    def test_double_dash2(self):
        options = Options()
        options.add_option(OptionBuilder.has_arg().create('n'))
        options.add_option(OptionBuilder.create('m'))

        try:
            self.parser.parse(options, ["-n", "--", "-m"])
            pytest.fail("MissingArgumentException not thrown for option -n")
        except MissingArgumentException as e:
            assert e.get_option() is not None, "option null"
            assert e.get_option().get_opt() == 'n', "n"

    def test_long_option_quote_handling(self):
        args = ["--bfile", "\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string", "Confirm --bfile \"arg\" strips quotes"

    def test_long_option_with_equals_quote_handling(self):
        args = ["--bfile=\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string", "Confirm --bfile=\"arg\" strips quotes"

    def test_long_with_equal_double_dash(self):
        args = ["--foo=bar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_arg().create('f'))

        cl = self.parser.parse(options, args)

        assert cl.get_option_value("foo") == "bar"
    
    def test_long_with_equal_single_dash(self):
        args = ["-foo=bar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_arg().create('f'))

        cl = self.parser.parse(options, args)

        assert cl.get_option_value("foo") == "bar"

    def test_long_without_equal_double_dash(self):
        args = ["--foobar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_arg().create('f'))

        cl = self.parser.parse(options, args, True)

        assert not cl.has_option("foo") # foo isn't expected to be recognized with a double dash

    def test_long_without_equal_single_dash(self):
        args = ["-foobar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_arg().create('f'))

        cl = self.parser.parse(options, args)

        assert cl.get_option_value("foo") == "bar"

    def test_long_with_unexpected_argument1(self):
        args = ["--foo=bar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").create('f'))

        try:
            cl = self.parser.parse(options, args)
        except UnrecognizedOptionException as e:
            assert e.get_option() == "--foo=bar"
            return

        pytest.fail("UnrecognizedOptionException not thrown")

    def test_long_with_unexpected_argument2(self):
        args = ["-foobar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").create('f'))

        try:
            self.parser.parse(options, args)
        except UnrecognizedOptionException as e:
            assert e.get_option() == "-foobar"
            return

        pytest.fail("UnrecognizedOptionException not thrown")
    
    def test_missing_arg(self):
        args = ["-b"]

        caught = False

        try:
            self.parser.parse(self.options, args)
        except MissingArgumentException as e:
            caught = True
            assert e.get_option().get_opt() == "b", "option missing an argument"

        assert caught, "Confirm MissingArgumentException caught"

    def test_missing_arg_with_bursting(self):
        args = ["-acb"]

        caught = False

        try:
            self.parser.parse(self.options, args)
        except MissingArgumentException as e:
            caught = True
            assert e.get_option().get_opt() == "b", "option missing an argument"

        assert caught, "Confirm MissingArgumentException caught"

    def test_missing_required_group(self):
        group = OptionGroup()
        group.add_option(OptionBuilder.create("a"))
        group.add_option(OptionBuilder.create("b"))
        group.set_required(True)

        options = Options()
        options.add_option_group(group)
        options.add_option(OptionBuilder.is_required().create("c"))

        try:
            self.parser.parse(options, ["-c"])
            pytest.fail("MissingOptionException not thrown")
        except MissingOptionException as e:
            assert len(e.get_missing_options()) == 1
            assert isinstance(e.get_missing_options()[0], OptionGroup)
        except ParseException as e:
            pytest.fail("Expected to catch MissingOptionException")
    
    def test_missing_required_option(self):
        args = ["-a"]

        options = Options()
        options.add_option("a", "enable-a", False, None)
        options.add_option(OptionBuilder.with_long_opt("bfile").has_arg().is_required().create('b'))

        try:
            self.parser.parse(options, args)
            pytest.fail("exception should have been thrown")
        except MissingOptionException as e:
            assert str(e) == "Missing required option: b", "Incorrect exception message"
            assert "b" in e.get_missing_options()
        except ParseException as e:
            pytest.fail("expected to catch MissingOptionException")

    def test_missing_required_options(self):
        args = ["-a"]

        options = Options()
        options.add_option("a", "enable-a", False, None)
        options.add_option(OptionBuilder.with_long_opt("bfile").has_arg().is_required().create('b'))
        options.add_option(OptionBuilder.with_long_opt("cfile").has_arg().is_required().create('c'))

        try:
            self.parser.parse(options, args)
            pytest.fail("exception should have been thrown")
        except MissingOptionException as e:
            assert str(e) == "Missing required options: b, c", "Incorrect exception message"
            assert "b" in e.get_missing_options()
            assert "c" in e.get_missing_options()
        except ParseException as e:
            pytest.fail("expected to catch MissingOptionException")

    def test_multiple(self):
        args = ["-c", "foobar", "-b", "toast"]

        cl = self.parser.parse(self.options, args, True)
        assert cl.has_option("c"), "Confirm -c is set"
        assert len(cl.get_arg_list()) == 3, "Confirm  3 extra args: " + str(len(cl.get_arg_list()))

        cl = self.parser.parse(self.options, cl.get_args())

        assert not cl.has_option("c"), "Confirm -c is not set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "toast", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 1, "Confirm  1 extra arg: " + str(len(cl.get_arg_list()))
        assert cl.get_arg_list()[0] == "foobar", "Confirm  value of extra arg: " + cl.get_arg_list()[0]\
        
    def test_multiple_with_long(self):
        args = ["--copt", "foobar", "--bfile", "toast"]

        cl = self.parser.parse(self.options, args, True)
        assert cl.has_option("c"), "Confirm -c is set"
        assert len(cl.get_arg_list()) == 3, "Confirm  3 extra args: " + str(len(cl.get_arg_list()))

        cl = self.parser.parse(self.options, cl.get_args())

        assert not cl.has_option("c"), "Confirm -c is not set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "toast", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 1, "Confirm  1 extra arg: " + str(len(cl.get_arg_list()))
        assert cl.get_arg_list()[0] == "foobar", "Confirm  value of extra arg: " + cl.get_arg_list()[0]
    
    def test_negative_argument(self):
        args = ["-b", "-1"]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "-1", "Confirm arg of -b is '-1'"

    def test_negative_option(self):
        args = ["-b", "-1"]

        self.options.add_option("1", False, None)

        cl = self.parser.parse(self.options, args)
        assert cl.get_option_value("b") == "-1"

    def test_option_and_required_option(self):
        args = ["-a", "-b", "file"]

        options = Options()
        options.add_option("a", "enable-a", False, None)
        options.add_option(OptionBuilder.with_long_opt("bfile").has_arg().is_required().create('b'))

        cl = self.parser.parse(options, args)

        assert cl.has_option("a"), "Confirm -a is set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "file", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 0, "Confirm NO of extra args"

    def test_option_group(self):
        group = OptionGroup()
        group.add_option(OptionBuilder.create("a"))
        group.add_option(OptionBuilder.create("b"))

        options = Options()
        options.add_option_group(group)

        cl = self.parser.parse(options, ["-b"])

        assert group.get_selected() == "b", "selected option"

    def test_option_group_long(self):
        group = OptionGroup()
        group.add_option(OptionBuilder.with_long_opt("foo").create())
        group.add_option(OptionBuilder.with_long_opt("bar").create())

        options = Options()
        options.add_option_group(group)

        cl = self.parser.parse(options, ["--bar"])

        assert cl.has_option("bar")
        assert group.get_selected() == "bar", "selected option"

    def test_partial_long_option_single_dash(self):
        args = ["-ver"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.has_arg().create('v'))

        cl = self.parser.parse(options, args)

        assert cl.has_option("version"), "Confirm --version is set"
        assert not cl.has_option("v"), "Confirm -v is not set"

    def test_properties_option1(self):
        args = ["-Jsource=1.5", "-J", "target", "1.5", "foo"]

        options = Options()
        options.add_option(OptionBuilder.with_value_separator().has_args(2).create('J'))

        cl = self.parser.parse(options, args)

        values = cl.get_option_values("J")
        assert values is not None, "null values"
        assert len(values) == 4, "number of values"
        assert values[0] == "source", "value 1"
        assert values[1] == "1.5", "value 2"
        assert values[2] == "target", "value 3"
        assert values[3] == "1.5", "value 4"

        argsleft = cl.get_arg_list()
        assert len(argsleft) == 1, "Should be 1 arg left"
        assert argsleft[0] == "foo", "Expecting foo"

    def test_properties_option2(self):
        args = ["-Dparam1", "-Dparam2=value2", "-D"]

        options = Options()
        options.add_option(OptionBuilder.with_value_separator().has_optional_args(2).create('D'))

        cl = self.parser.parse(options, args)

        props = cl.get_option_properties("D")
        assert props is not None, "null properties"
        assert len(props) == 2, "number of properties in " + props
        assert props["param1"] == "true", "property 1"
        assert props["param2"] == "value2", "property 2"

        argsleft = cl.get_arg_list()
        assert len(argsleft) == 0, "Should be no arg left"

    def test_property_option_flags(self):
        opts = Options()
        opts.add_option("a", False, "toggle -a")
        opts.add_option("c", "c", False, "toggle -c")
        opts.add_option(OptionBuilder.has_optional_arg().create('e'))

        properties = {"a": "true", "c": "yes", "e": "1"}

        cmd = self.parse(self.parser, opts, None, properties)
        assert cmd.has_option("a")
        assert cmd.has_option("c")
        assert cmd.has_option("e")

        properties = {"a": "false", "c": "no", "e": "0"}

        cmd = self.parse(self.parser, opts, None, properties)
        assert not cmd.has_option("a")
        assert not cmd.has_option("c")
        assert cmd.has_option("e") # this option accepts an argument

        properties = {"a": "TRUE", "c": "nO", "e": "TrUe"}

        cmd = self.parse(self.parser, opts, None, properties)
        assert cmd.has_option("a")
        assert not cmd.has_option("c")
        assert cmd.has_option("e")

        properties = {"a": "just a string", "e": ""}

        cmd = self.parse(self.parser, opts, None, properties)
        assert not cmd.has_option("a")
        assert not cmd.has_option("c")
        assert cmd.has_option("e")

        properties = {"a": "0", "c": "1"}

        cmd = self.parse(self.parser, opts, None, properties)
        assert not cmd.has_option("a")
        assert cmd.has_option("c")

    def test_property_option_group(self):
        opts = Options()

        group1 = OptionGroup()
        group1.add_option(OptionBuilder.create("a"))
        group1.add_option(OptionBuilder.create("b"))
        opts.add_option_group(group1)

        group2 = OptionGroup()
        group2.add_option(OptionBuilder.create("x"))
        group2.add_option(OptionBuilder.create("y"))
        opts.add_option_group(group2)

        args = ["-a"]

        properties = {"b": "true", "x": "true"}

        cmd = self.parse(self.parser, opts, args, properties)

        assert cmd.has_option("a")
        assert not cmd.has_option("b")
        assert cmd.has_option("x")
        assert not cmd.has_option("y")

    def test_property_option_multiple_values(self):
        opts = Options()
        opts.add_option(OptionBuilder.has_args().with_value_separator(',').create('k'))

        properties = {"k": "one,two"}

        values = ["one", "two"]

        cmd = self.parse(self.parser, opts, None, properties)
        assert cmd.has_option("k")
        assert cmd.get_option_values("k") == values
    
    def test_property_option_required(self):
        opts = Options()
        opts.add_option(OptionBuilder.is_required().create('f'))

        properties = {"f": "true"}

        cmd = self.parse(self.parser, opts, None, properties)
        assert cmd.has_option("f")

    def test_property_option_singular_value(self):
        opts = Options()
        opts.add_option(OptionBuilder.has_optional_args(2).with_long_opt("hide").create())

        properties = {"hide": "seek"}

        cmd = self.parse(self.parser, opts, None, properties)
        assert cmd.has_option("hide")
        assert cmd.get_option_value("hide") == "seek"
        assert not cmd.has_option("fake")

    def test_property_option_unexpected(self):
        opts = Options()

        properties = {"f": "true"}

        try:
            self.parse(self.parser, opts, None, properties)
            pytest.fail("UnrecognizedOptionException expected")
        except UnrecognizedOptionException as e:
            pass # expected

    def test_property_override_values(self):
        opts = Options()
        opts.add_option(OptionBuilder.has_optional_args(2).create('i'))
        opts.add_option(OptionBuilder.has_optional_args().create('j'))

        args = ["-j", "found", "-i", "ink"]

        properties = {"j": "seek"}

        cmd = self.parse(self.parser, opts, args, properties)
        assert cmd.has_option("j")
        assert cmd.get_option_value("j") == "found"
        assert cmd.has_option("i")
        assert cmd.get_option_value("i") == "ink"
        assert not cmd.has_option("fake")

    def test_reuse_options_twice(self):
        opts = Options()
        opts.add_option(OptionBuilder.is_required().create('v'))

        # first parsing
        self.parser.parse(opts, ["-v"])

        try:
            # second parsing, with the same Options instance and an invalid command line
            self.parser.parse(opts, [])
            pytest.fail("MissingOptionException not thrown")
        except MissingOptionException as e:
            pass # expected

    def test_short_option_concatenated_quote_handling(self):
        args = ["-b\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string", "Confirm -b\"arg\" strips quotes"

    def test_short_option_quote_handling(self):
        args = ["-b", "\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string", "Confirm -b \"arg\" strips quotes"

    def test_short_with_equal(self):
        args = ["-f=bar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_arg().create('f'))

        cl = self.parser.parse(options, args)

        assert cl.get_option_value("foo") == "bar"

    def test_short_without_equal(self):
        args = ["-fbar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").has_arg().create('f'))

        cl = self.parser.parse(options, args)

        assert cl.get_option_value("foo") == "bar"

    def test_short_with_unexpected_argument(self):
        args = ["-f=bar"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("foo").create('f'))

        try:
            self.parser.parse(options, args)
        except UnrecognizedOptionException as e:
            assert e.get_option() == "-f=bar"
            return

        pytest.fail("UnrecognizedOptionException not thrown")

    def test_simple_long(self):
        args = ["--enable-a", "--bfile", "toast", "foo", "bar"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("a"), "Confirm -a is set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "toast", "Confirm arg of -b"
        assert cl.get_option_value("bfile") == "toast", "Confirm arg of --bfile"
        assert len(cl.get_arg_list()) == 2, "Confirm size of extra args"

    def test_simple_short(self):
        args = ["-a", "-b", "toast", "foo", "bar"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("a"), "Confirm -a is set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "toast", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 2, "Confirm size of extra args"

    def test_single_dash(self):
        args = ["--copt", "-b", "-", "-a", "-"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("a"), "Confirm -a is set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "-", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 1, "Confirm 1 extra arg: " + str(len(cl.get_arg_list()))
        assert cl.get_arg_list()[0] == "-", "Confirm value of extra arg: " + cl.get_arg_list()[0]
    
    def test_stop_at_expected_arg(self):
        args = ["-b", "foo"]

        cl = self.parser.parse(self.options, args, True)

        assert cl.has_option('b'), "Confirm -b is set"
        assert cl.get_option_value('b') == "foo", "Confirm -b is set"
        assert len(cl.get_arg_list()) == 0, "Confirm no extra args: " + str(len(cl.get_arg_list()))

    def test_stop_at_non_option_long(self):
        args = ["--zop==1", "-abtoast", "--b=bar"]

        cl = self.parser.parse(self.options, args, True)

        assert not cl.has_option("a"), "Confirm -a is not set"
        assert not cl.has_option("b"), "Confirm -b is not set"
        assert len(cl.get_arg_list()) == 3, "Confirm 3 extra args: " + str(len(cl.get_arg_list()))

    def test_stop_at_non_option_short(self):
        args = ["-z", "-a", "-btoast"]

        cl = self.parser.parse(self.options, args, True)
        assert not cl.has_option("a"), "Confirm -a is not set"
        assert len(cl.get_arg_list()) == 3, "Confirm 3 extra args: " + str(len(cl.get_arg_list()))

    def test_stop_at_unexpected_arg(self):
        args = ["-c", "foober", "-b", "toast"]

        cl = self.parser.parse(self.options, args, True)
        assert cl.has_option("c"), "Confirm -c is set"
        assert len(cl.get_arg_list()) == 3, "Confirm 3 extra args: " + str(len(cl.get_arg_list()))

    def test_stop_bursting(self):
        args = ["-azc"]

        cl = self.parser.parse(self.options, args, True)
        assert cl.has_option("a"), "Confirm -a is set"
        assert not cl.has_option("c"), "Confirm -c is not set"

        assert len(cl.get_arg_list()) == 1, "Confirm 1 extra arg: " + str(len(cl.get_arg_list()))
        assert cl.get_arg_list()[0] == "zc", "Confirm value of extra arg: " + cl.get_arg_list()[0]

    def test_stop_bursting2(self):
        args = ["-c", "foobar", "-btoast"]

        cl = self.parser.parse(self.options, args, True)
        assert cl.has_option("c"), "Confirm -c is set"
        assert len(cl.get_arg_list()) == 2, "Confirm 2 extra args: " + str(len(cl.get_arg_list()))

        cl = self.parser.parse(self.options, cl.get_args())

        assert not cl.has_option("c"), "Confirm -c is not set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "toast", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 1, "Confirm 1 extra arg: " + str(len(cl.get_arg_list()))
        assert cl.get_arg_list()[0] == "foobar", "Confirm value of extra arg: " + cl.get_arg_list()[0]

    def test_unambiguous_partial_long_option1(self):
        args = ["--ver"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("help").create())

        cl = self.parser.parse(options, args)

        assert cl.has_option("version"), "Confirm --version is set"

    def test_unambiguous_partial_long_option2(self):
        args = ["--ver"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("help").create())

        cl = self.parser.parse(options, args)

        assert cl.has_option("version"), "Confirm --version is set"

    def test_unambiguous_partial_long_option3(self):
        args = ["--ver=1"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("verbose").has_optional_arg().create())
        options.add_option(OptionBuilder.with_long_opt("help").create())

        cl = self.parser.parse(options, args)

        assert cl.has_option("verbose"), "Confirm --verbose is set"
        assert cl.get_option_value("verbose") == "1"

    def test_unambiguous_partial_long_option4(self):
        args = ["--ver=1"]

        options = Options()
        options.add_option(OptionBuilder.with_long_opt("verbose").has_optional_arg().create())
        options.add_option(OptionBuilder.with_long_opt("help").create())

        cl = self.parser.parse(options, args)

        assert cl.has_option("verbose"), "Confirm --verbose is set"
        assert cl.get_option_value("verbose") == "1"

    def test_unlimited_args(self):
        args = ["-e", "one", "two", "-f", "alpha"]

        options = Options()
        options.add_option(OptionBuilder.has_args().create('e'))
        options.add_option(OptionBuilder.has_args().create('f'))

        cl = self.parser.parse(options, args)

        assert cl.has_option("e"), "Confirm -e is set"
        assert len(cl.get_option_values("e")) == 2, "number of arg for -e"
        assert cl.has_option("f"), "Confirm -f is set"
        assert len(cl.get_option_values("f")) == 1, "number of arg for -f"

    def test_unrecognized_option(self):
        args = ["-a", "-d", "-b", "toast", "foo", "bar"]

        try:
            self.parser.parse(self.options, args)
            pytest.fail("UnrecognizedOptionException wasn't thrown")
        except UnrecognizedOptionException as e:
            assert e.get_option() == "-d"

    def test_unrecognized_option_with_bursting(self):
        args = ["-adbtoast", "foo", "bar"]

        try:
            self.parser.parse(self.options, args)
            pytest.fail("UnrecognizedOptionException wasn't thrown")
        except UnrecognizedOptionException as e:
            assert e.get_option() == "-adbtoast"

    def test_with_required_option(self):
        args = ["-b", "file"]

        options = Options()
        options.add_option("a", "enable-a", False, None)
        options.add_option(OptionBuilder.with_long_opt("bfile").has_arg().is_required().create('b'))

        cl = self.parser.parse(options, args)

        assert not cl.has_option("a"), "Confirm -a is NOT set"
        assert cl.has_option("b"), "Confirm -b is set"
        assert cl.get_option_value("b") == "file", "Confirm arg of -b"
        assert len(cl.get_arg_list()) == 0, "Confirm NO of extra args"
