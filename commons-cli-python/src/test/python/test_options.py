import pytest
from main.python.options import Options
from main.python.option_builder import OptionBuilder
from main.python.option_group import OptionGroup
from main.python.posix_parser import PosixParser
from main.python.missing_option_exception import MissingOptionException

class TestOptions:

    def test_duplicate_long(self):
        opts = Options()
        opts.add_option("a", "--a", False, "toggle -a")
        opts.add_option("a", "--a", False, "toggle -a*")
        assert "toggle -a*" == opts.get_option("a").get_description(), "last one in wins"

    def test_duplicate_simple(self):
        opts = Options()
        opts.add_option("a", False, "toggle -a")
        opts.add_option("a", True, "toggle -a*")
        assert "toggle -a*" == opts.get_option("a").get_description(), "last one in wins"

    def test_get_matching_opts(self):
        options = Options()
        options.add_option(OptionBuilder.with_long_opt("version").create())
        options.add_option(OptionBuilder.with_long_opt("verbose").create())

        assert len(options.get_matching_options("foo")) == 0
        assert 1 == len(options.get_matching_options("version"))
        assert 2 == len(options.get_matching_options("ver"))

    def test_get_options_groups(self):
        options = Options()

        group1 = OptionGroup()
        group1.add_option(OptionBuilder.create('a'))
        group1.add_option(OptionBuilder.create('b'))

        group2 = OptionGroup()
        group2.add_option(OptionBuilder.create('x'))
        group2.add_option(OptionBuilder.create('y'))

        options.add_option_group(group1)
        options.add_option_group(group2)

        assert options.get_option_groups() is not None
        assert 2 == len(options.get_option_groups())
        
    def test_help_options(self):
        long_only1 = OptionBuilder.with_long_opt("long-only1").create()
        long_only2 = OptionBuilder.with_long_opt("long-only2").create()
        short_only1 = OptionBuilder.create("1")
        short_only2 = OptionBuilder.create("2")
        bothA = OptionBuilder.with_long_opt("bothA").create("a")
        bothB = OptionBuilder.with_long_opt("bothB").create("b")

        options = Options()
        options.add_option(long_only1)
        options.add_option(long_only2)
        options.add_option(short_only1)
        options.add_option(short_only2)
        options.add_option(bothA)
        options.add_option(bothB)

        all_options = []
        all_options.append(long_only1)
        all_options.append(long_only2)
        all_options.append(short_only1)
        all_options.append(short_only2)
        all_options.append(bothA)
        all_options.append(bothB)

        help_options = options.help_options()

        assert all(x in help_options for x in all_options), "Everything in all should be in help"
        assert all(x in all_options for x in help_options), "Everything in help should be in all"

    def test_long(self):
        opts = Options()

        opts.add_option("a", "--a", False, "toggle -a")
        opts.add_option("b", "--b", True, "set -b")

        assert opts.has_option("a")
        assert opts.has_option("b")

    def test_missing_option_exception(self):
        options = Options()
        options.add_option(OptionBuilder.is_required().create("f"))
        with pytest.raises(MissingOptionException) as e:
            PosixParser().parse(options, [])
        assert "Missing required option: f" == str(e.value)

    def test_missing_options_exception(self):
        options = Options()
        options.add_option(OptionBuilder.is_required().create("f"))
        options.add_option(OptionBuilder.is_required().create("x"))
        with pytest.raises(MissingOptionException) as e:
            PosixParser().parse(options, [])
        assert "Missing required options: f, x" == str(e.value)

    def test_simple(self):
        opts = Options()

        opts.add_option("a", False, "toggle -a")
        opts.add_option("b", True, "toggle -b")

        assert opts.has_option("a")
        assert opts.has_option("b")

    def test_to_string(self):
        options = Options()
        options.add_option("f", "foo", True, "Foo")
        options.add_option("b", "bar", False, "Bar")

        s = str(options)
        assert s is not None, "null string returned"
        assert "foo" in s.lower(), "foo option missing"
        assert "bar" in s.lower(), "bar option missing"
