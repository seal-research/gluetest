import pytest
from main.python.default_parser import DefaultParser
from parser_test_case import ParserTestCase

class TestDefaultParser(ParserTestCase):
    @pytest.fixture(autouse=True)
    def set_up(self):
        self._set_up()
        self.parser = DefaultParser()

    def test_builder(self):
        self.parser = DefaultParser.builder() \
            .set_strip_leading_and_trailing_quotes(False) \
            .set_allow_partial_matching(False) \
            .build()
        assert isinstance(self.parser, DefaultParser)

    def test_long_option_quote_handling_without_strip(self):
        self.parser = DefaultParser.builder().set_strip_leading_and_trailing_quotes(False).build()
        args = ["--bfile", "\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "\"quoted string\""

    def test_long_option_quote_handling_with_strip(self):
        self.parser = DefaultParser.builder().set_strip_leading_and_trailing_quotes(True).build()
        args = ["--bfile", "\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string"

    def test_long_option_with_equals_quote_handling(self):
        args = ["--bfile=\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "\"quoted string\""

    def test_long_option_with_equals_quote_handling_without_strip(self):
        self.parser = DefaultParser.builder().set_strip_leading_and_trailing_quotes(False).build()
        args = ["--bfile=\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "\"quoted string\""

    def test_long_option_with_equals_quote_handling_with_strip(self):
        self.parser = DefaultParser.builder().set_strip_leading_and_trailing_quotes(True).build()
        args = ["--bfile=\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string"

    def test_short_option_concatenated_quote_handling(self):
        args = ["-b\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "\"quoted string\""

    def test_short_option_quote_handling_without_strip(self):
        self.parser = DefaultParser.builder().set_strip_leading_and_trailing_quotes(False).build()
        args = ["-b", "\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "\"quoted string\""

    def test_short_option_quote_handling_with_strip(self):
        self.parser = DefaultParser.builder().set_strip_leading_and_trailing_quotes(True).build()
        args = ["-b", "\"quoted string\""]

        cl = self.parser.parse(self.options, args)

        assert cl.get_option_value("b") == "quoted string"
