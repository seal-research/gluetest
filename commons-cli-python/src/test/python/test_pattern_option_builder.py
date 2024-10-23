from main.python.pattern_option_builder import PatternOptionBuilder
from main.python.posix_parser import PosixParser
from main.python.type_handler import TypeHandler
from main.python.missing_option_exception import MissingOptionException
from urllib.parse import urlparse
from calendar import Calendar
from datetime import datetime
from pathlib import Path
import io
import os
import pytest


class AbstractCalendar:

    def __init__(self):
        raise AttributeError("Abstract class")
    
    def get_instance(self):
        return Calendar()


class TestPatternOptionBuilder:
    
    @pytest.fixture(autouse=True)
    def set_up(self):
        TypeHandler.update_namespace_classes(self, globals())

    def test_class_pattern(self):
        options = PatternOptionBuilder.parse_pattern("c+d+")
        parser = PosixParser()
        line = parser.parse(options, ["-c", "AbstractCalendar", "-d", "Undefined.DateTime"])

        assert line.get_option_object("c") == AbstractCalendar, "c value"
        assert line.get_option_object("d") is None, "d value"

    def test_empty_pattern(self):
        options = PatternOptionBuilder.parse_pattern("")
        assert len(options.get_options()) == 0

    def test_existing_file_pattern(self):
        # Create a file
        open('existing-readable.file', 'x').close()

        options = PatternOptionBuilder.parse_pattern("g<")
        parser = PosixParser()
        line = parser.parse(options, ["-g", "existing-readable.file"])

        parsed_readable_file_stream = line.get_option_object("g")

        assert parsed_readable_file_stream is not None, "option g not parsed"
        assert isinstance(parsed_readable_file_stream, io.TextIOWrapper), "option g not io.TextIOWrapper"

        # Clean up
        parsed_readable_file_stream.close()
        os.remove("existing-readable.file")

    def test_existing_file_pattern_file_not_exist(self):
        options = PatternOptionBuilder.parse_pattern("f<")
        parser = PosixParser()
        line = parser.parse(options, ["-f", "non-existing.file"])

        assert line.get_option_object("f") is None, "option f not None"

    def test_number_pattern(self):
        options = PatternOptionBuilder.parse_pattern("n%d%x%")
        parser = PosixParser()
        line = parser.parse(options, ["-n", "1", "-d", "2.1", "-x", "3,5"])

        assert line.get_option_object("n").__class__ == int, "n object class" 
        assert line.get_option_object("n") == 1, "n value"

        assert line.get_option_object("d").__class__ == float, "d object class"
        assert line.get_option_object("d") == 2.1, "d value"

        assert line.get_option_object("x") is None, "x object"

    def test_object_pattern(self):
        options = PatternOptionBuilder.parse_pattern("o@i@n@")
        parser = PosixParser()
        line = parser.parse(options, ["-o", "str", "-i", "AbstractCalendar", "-n", "Undefined.DateTime"])

        assert line.get_option_object("o") == "", "o value"
        assert line.get_option_object("i") is None, "i value"
        assert line.get_option_object("n") is None, "n value"

    def test_required_option(self):
        options = PatternOptionBuilder.parse_pattern("!n%m%")
        parser = PosixParser()

        try:
            parser.parse(options, [""])
            pytest.fail("MissingOptionException wasn't thrown")
        except MissingOptionException as e:
            assert 1 == len(e.get_missing_options())
            assert "n" in e.get_missing_options()

    def test_simple_pattern(self):
        options = PatternOptionBuilder.parse_pattern("a:b@cde>f+n%t/m*z#")
        args = ["-c", "-a", "foo", "-b", "list", "-e", "build.xml", "-f", "AbstractCalendar", "-n", "4.5", "-t", "https://commons.apache.org", "-z", "Thu Jun 06 17:48:57 EDT 2002", "-m", "test*"]

        parser = PosixParser()
        line = parser.parse(options, args)

        assert line.get_option_value("a") == "foo", "flag a"
        assert line.get_option_object("a") == "foo", "string flag a"
        assert line.get_option_object("b") == list(), "option flag b"
        assert line.has_option("c"), "boolean true flag c"
        assert not line.has_option("d"), "boolean false flag d"
        assert line.get_option_object("e") == Path("build.xml"), "file flag e"
        assert line.get_option_object("f") == AbstractCalendar, "class flag f"
        assert line.get_option_object("n") == 4.5, "number flag n"
        assert line.get_option_object("t") == urlparse("https://commons.apache.org"), "url flag t"

        # tests the char methods of CommandLine that delegate to the String methods
        assert line.get_option_value('a') == "foo", "flag a"
        assert line.get_option_object('a') == "foo", "string flag a"
        assert line.get_option_object('b') == list(), "option flag b"
        assert line.has_option('c'), "boolean true flag c"
        assert not line.has_option('d'), "boolean false flag d"
        assert line.get_option_object('e') == Path("build.xml"), "file flag e"
        assert line.get_option_object('f') == AbstractCalendar, "class flag f"
        assert line.get_option_object('n') == 4.5, "number flag n"
        assert line.get_option_object('t') == urlparse("https://commons.apache.org"), "url flag t"

        # FILES NOT SUPPORTED YET
        try:
            assert line.get_option_object('m') == [], "multiple files flag m"
            pytest.fail("Multiple files are not supported yet, should have failed")
        except ValueError as uoe:
            pass

        # DATES NOT SUPPORTED YET
        try:
            assert line.get_option_object('z') == datetime(1023400137276), "date flag z"
            pytest.fail("Date is not supported yet, should have failed")
        except ValueError as uoe:
            pass

    def test_untyped_pattern(self):
        options = PatternOptionBuilder.parse_pattern("abc")
        parser = PosixParser()
        line = parser.parse(options, ["-abc"])

        assert line.has_option("a")
        assert line.get_option_object("a") is None, "a value"
        assert line.has_option("b")
        assert line.get_option_object("b") is None, "b value"
        assert line.has_option("c")
        assert line.get_option_object("c") is None, "c value"

    def test_URL_pattern(self):
        options = PatternOptionBuilder.parse_pattern("u/v/")
        parser = PosixParser()
        line = parser.parse(options, ["-u", "https://commons.apache.org", "-v", "foo://commons.apache.org"])

        assert line.get_option_object("u") == urlparse("https://commons.apache.org"), "u value"
        assert line.get_option_object("v") is None, "v value"
