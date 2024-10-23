import pytest
from main.python.option_group import OptionGroup
from main.python.option import Option
from main.python.options import Options
from main.python.option_builder import OptionBuilder
from main.python.posix_parser import PosixParser
from main.python.already_selected_exception import AlreadySelectedException

class TestOptionGroup:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.parser = PosixParser()

        file = Option("f", "file", False, "file to process")
        dir = Option("d", "directory", False, "directory to process")
        group = OptionGroup()
        group.add_option(file)
        group.add_option(dir)
        self.options = Options().add_option_group(group)

        section = Option("s", "section", False, "section to process")
        chapter = Option("c", "chapter", False, "chapter to process")
        group2 = OptionGroup()
        group2.add_option(section)
        group2.add_option(chapter)

        self.options.add_option_group(group2)

        importOpt = Option(None, "import", False, "section to process")
        exportOpt = Option(None, "export", False, "chapter to process")
        group3 = OptionGroup()
        group3.add_option(importOpt)
        group3.add_option(exportOpt)
        self.options.add_option_group(group3)

        self.options.add_option("r", "revision", False, "revision number")

    def test_get_names(self):
        group = OptionGroup()
        group.add_option(OptionBuilder.create("a"))
        group.add_option(OptionBuilder.create("b"))

        assert group.get_names() is not None, "None names"
        assert len(group.get_names()) == 2
        assert "a" in group.get_names()
        assert "b" in group.get_names()

    def test_no_options_extra_args(self):
        args = ["arg1", "arg2"]

        cl = self.parser.parse(self.options, args)

        assert not cl.has_option("r"), "Confirm -r is NOT set"
        assert not cl.has_option("f"), "Confirm -f is NOT set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert not cl.has_option("s"), "Confirm -s is NOT set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 2, "Confirm TWO extra args"

    def test_single_long_option(self):
        args = ["--file"]

        cl = self.parser.parse(self.options, args)

        assert not cl.has_option("r"), "Confirm -r is NOT set"
        assert cl.has_option("f"), "Confirm -f is set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert not cl.has_option("s"), "Confirm -s is NOT set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 0, "Confirm no extra args"

    def test_single_option(self):
        args = ["-r"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("r"), "Confirm -r is set"
        assert not cl.has_option("f"), "Confirm -f is NOT set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert not cl.has_option("s"), "Confirm -s is NOT set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 0, "Confirm no extra args"

    def test_single_option_from_group(self):
        args = ["-f"]

        cl = self.parser.parse(self.options, args)

        assert not cl.has_option("r"), "Confirm -r is NOT set"
        assert cl.has_option("f"), "Confirm -f is set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert not cl.has_option("s"), "Confirm -s is NOT set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 0, "Confirm no extra args"
    
    def test_to_string(self):
        group1 = OptionGroup()
        group1.add_option(Option(None, "foo", False, "Foo"))
        group1.add_option(Option(None, "bar", False, "Bar"))

        if not "[--bar Bar, --foo Foo]" == str(group1):
            assert "[--foo Foo, --bar Bar]" == str(group1)

        group2 = OptionGroup()
        group2.add_option(Option("f", "foo", False, "Foo"))
        group2.add_option(Option("b", "bar", False, "Bar"))

        if not "[-b Bar, -f Foo]" == str(group2):
            assert "[-f Foo, -b Bar]" == str(group2)

    def test_two_long_options_from_group(self):
        args = ["--file", "--directory"]

        with pytest.raises(AlreadySelectedException) as e:
            self.parser.parse(self.options, args)
        assert e.value.get_option_group() is not None, "null option group"
        assert e.value.get_option_group().get_selected() == "f", "selected option"
        assert e.value.get_option().get_opt() == "d", "option"

    def test_two_options_from_different_group(self):
        args = ["-f", "-s"]

        cl = self.parser.parse(self.options, args)

        assert not cl.has_option("r"), "Confirm -r is NOT set"
        assert cl.has_option("f"), "Confirm -f is set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert cl.has_option("s"), "Confirm -s is set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 0, "Confirm NO extra args"

    def test_two_options_from_group(self):
        args = ["-f", "-d"]

        with pytest.raises(AlreadySelectedException) as e:
            self.parser.parse(self.options, args)
        assert e.value.get_option_group() is not None, "null option group"
        assert e.value.get_option_group().get_selected() == "f", "selected option"
        assert e.value.get_option().get_opt() == "d", "option"
    
    def test_two_options_from_group_with_properties(self):
        args = ["-f"]

        properties = {}
        properties["d"] = "true"

        cl = self.parser.parse(self.options, args, properties)
        assert cl.has_option("f")
        assert not cl.has_option("d")

    def test_two_valid_long_options(self):
        args = ["--revision", "--file"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("r"), "Confirm -r is set"
        assert cl.has_option("f"), "Confirm -f is set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert not cl.has_option("s"), "Confirm -s is NOT set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 0, "Confirm no extra args"

    def test_two_valid_options(self):
        args = ["-r", "-f"]

        cl = self.parser.parse(self.options, args)

        assert cl.has_option("r"), "Confirm -r is set"
        assert cl.has_option("f"), "Confirm -f is set"
        assert not cl.has_option("d"), "Confirm -d is NOT set"
        assert not cl.has_option("s"), "Confirm -s is NOT set"
        assert not cl.has_option("c"), "Confirm -c is NOT set"
        assert len(cl.get_arg_list()) == 0, "Confirm no extra args"
    
    def test_valid_long_only_options(self):
        cl1 = self.parser.parse(self.options, ["--export"])
        assert cl1.has_option("export"), "Confirm --export is set"

        cl2 = self.parser.parse(self.options, ["--import"])
        assert cl2.has_option("import"), "Confirm --import is set"
