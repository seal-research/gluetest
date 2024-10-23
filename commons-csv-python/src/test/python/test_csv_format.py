import pytest
import pickle
from io import BytesIO
import os
from enum import Enum
from main.python.csv_format import CSVFormat
from main.python.quote_mode import QuoteMode
from main.python.constants import Constants


class TestCSVFormat:

    class EmptyEnum(Enum):
        pass

    class Header(Enum):
        Name = 1
        Email = 2
        Phone = 3

    @staticmethod
    def assert_not_equals(right: object, left: object):
        assert not right == left
        assert not left == right

    @staticmethod
    def copy(formatter: CSVFormat):
        return formatter.with_delimiter(formatter.get_delimiter())

    def test_delimiter_same_as_comment_start_throws_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_delimiter("!").with_comment_marker("!")

    def test_delimiter_same_as_escape_throws_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_delimiter("!").with_escape("!")

    def test_duplicate_header_elements(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_header("A", "A")

    def test_equals(self):
        right = CSVFormat.DEFAULT
        left = self.copy(right)
        assert right == right
        assert right == left
        assert left == right
        assert hash(right) == hash(right)
        assert hash(right) == hash(left)

    def test_equals_comment_start(self):
        right = (
            CSVFormat.new_format("'")
            .with_quote('"')
            .with_comment_marker("#")
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_comment_marker("!")
        self.assert_not_equals(right, left)

    def test_equals_delimiter(self):
        right = CSVFormat.new_format("!")
        left = CSVFormat.new_format("?")
        self.assert_not_equals(right, left)

    def test_equals_escape(self):
        right = (
            CSVFormat.new_format("'")
            .with_quote('"')
            .with_comment_marker("#")
            .with_escape("+")
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_escape("!")
        self.assert_not_equals(right, left)

    def test_equals_header(self):
        right = (
            CSVFormat.new_format("'")
            .with_record_separator(Constants.CR)
            .with_comment_marker("#")
            .with_escape("+")
            .with_header("One", "Two", "Three")
            .with_ignore_empty_lines()
            .with_ignore_surrounding_spaces()
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_header("Three", "Two", "One")
        self.assert_not_equals(right, left)

    def test_equals_ignore_empty_lines(self):
        right = (
            CSVFormat.new_format("'")
            .with_comment_marker("#")
            .with_escape("+")
            .with_ignore_empty_lines()
            .with_ignore_surrounding_spaces()
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_ignore_empty_lines(False)
        self.assert_not_equals(right, left)

    def test_equals_ignore_surrounding_spaces(self):
        right = (
            CSVFormat.new_format("'")
            .with_comment_marker("#")
            .with_escape("+")
            .with_ignore_surrounding_spaces()
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_ignore_surrounding_spaces(False)
        assert right != left

    def test_equals_left_no_quote_right_quote(self):
        left = CSVFormat.new_format(",").with_quote(None)
        right = left.with_quote("#")
        assert left != right

    def test_equals_no_quotes(self):
        left = CSVFormat.new_format(",").with_quote(None)
        right = left.with_quote(None)
        assert left == right

    def test_equals_null_string(self):
        right = (
            CSVFormat.new_format("'")
            .with_record_separator(Constants.CR)
            .with_comment_marker("#")
            .with_escape("+")
            .with_ignore_empty_lines()
            .with_ignore_surrounding_spaces()
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
            .with_null_string("null")
        )
        left = right.with_null_string("---")
        assert right != left

    def test_equals_one(self):
        csv_format_one = CSVFormat.INFORMIX_UNLOAD
        csv_format_two = CSVFormat.MYSQL
        assert csv_format_one.get_escape_character() == "\\"
        assert csv_format_one.get_quote_mode() is None
        assert csv_format_one.get_ignore_empty_lines()
        assert not csv_format_one.get_skip_header_record()
        assert not csv_format_one.get_ignore_header_case()
        assert csv_format_one.get_comment_marker() is None
        assert not csv_format_one.is_comment_marker_set()
        assert csv_format_one.is_quote_character_set()
        assert csv_format_one.get_delimiter() == "|"
        assert not (
            csv_format_one
            .get_allow_missing_column_names()
        )
        assert csv_format_one.is_escape_character_set()
        assert csv_format_one.get_record_separator() == "\n"
        assert csv_format_one.get_quote_character() == '"'
        assert not csv_format_one.get_trailing_delimiter()
        assert not csv_format_one.get_trim()
        assert not csv_format_one.is_null_string_set()
        assert csv_format_one.get_null_string() is None
        assert not csv_format_one.get_ignore_surrounding_spaces()
        assert csv_format_two.is_escape_character_set()
        assert csv_format_two.get_quote_character() is None
        assert not csv_format_two.get_allow_missing_column_names()
        assert (
                       csv_format_two.get_quote_mode()
                       == QuoteMode.ALL_NON_NULL
        )
        assert csv_format_two.get_delimiter() == "\t"
        assert csv_format_two.get_record_separator() == "\n"
        assert not csv_format_two.is_quote_character_set()
        assert csv_format_two.is_null_string_set()
        assert csv_format_two.get_escape_character() == "\\"
        assert not csv_format_two.get_ignore_header_case()
        assert not csv_format_two.get_trim()
        assert not csv_format_two.get_ignore_empty_lines()
        assert csv_format_two.get_null_string() == "\\N"
        assert not csv_format_two.get_ignore_surrounding_spaces()
        assert not csv_format_two.get_trailing_delimiter()
        assert not csv_format_two.get_skip_header_record()
        assert csv_format_two.get_comment_marker() is None
        assert not csv_format_two.is_comment_marker_set()
        assert csv_format_two != csv_format_one
        assert not csv_format_two == csv_format_one
        assert csv_format_one.get_escape_character() == "\\"
        assert csv_format_one.get_quote_mode() is None
        assert csv_format_one.get_ignore_empty_lines()
        assert not csv_format_one.get_skip_header_record()
        assert not csv_format_one.get_ignore_header_case()
        assert csv_format_one.get_comment_marker() is None
        assert not csv_format_one.is_comment_marker_set()
        assert csv_format_one.is_quote_character_set()
        assert csv_format_one.get_delimiter() == "|"
        assert not (
            csv_format_one
            .get_allow_missing_column_names()
        )
        assert csv_format_one.is_escape_character_set()
        assert csv_format_one.get_record_separator() == "\n"
        assert csv_format_one.get_quote_character() == '"'
        assert not csv_format_one.get_trailing_delimiter()
        assert not csv_format_one.get_trim()
        assert not csv_format_one.is_null_string_set()
        assert csv_format_one.get_null_string() is None
        assert not (
            csv_format_one
            .get_ignore_surrounding_spaces()
        )
        assert csv_format_two.is_escape_character_set()
        assert csv_format_two.get_quote_character() is None
        assert not csv_format_two.get_allow_missing_column_names()
        assert (
                       csv_format_two.get_quote_mode()
                       == QuoteMode.ALL_NON_NULL
        )
        assert csv_format_two.get_delimiter() == "\t"
        assert csv_format_two.get_record_separator() == "\n"
        assert not csv_format_two.is_quote_character_set()
        assert csv_format_two.is_null_string_set()
        assert csv_format_two.get_escape_character() == "\\"
        assert not csv_format_two.get_ignore_header_case()
        assert not csv_format_two.get_trim()
        assert not csv_format_two.get_ignore_empty_lines()
        assert csv_format_two.get_null_string() == "\\N"
        assert not (
            csv_format_two
            .get_ignore_surrounding_spaces()
        )
        assert not csv_format_two.get_trailing_delimiter()
        assert not csv_format_two.get_skip_header_record()
        assert csv_format_two.get_comment_marker() is None
        assert not csv_format_two.is_comment_marker_set()
        assert csv_format_two != csv_format_one
        assert csv_format_two != csv_format_one
        assert not csv_format_two == csv_format_one
        assert csv_format_one != csv_format_two
        assert csv_format_two != csv_format_one
        assert not csv_format_two == csv_format_one

    def test_equals_quote_char(self):
        right = CSVFormat.new_format("'").with_quote('"')
        left = right.with_quote("!")
        assert right != left

    def test_equals_quote_policy(self):
        right = (
            CSVFormat.new_format("'")
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_quote_mode(QuoteMode.MINIMAL)
        assert right != left

    def test_equals_record_separator(self):
        right = (
            CSVFormat.new_format("'")
            .with_record_separator(Constants.CR)
            .with_comment_marker("#")
            .with_escape("+")
            .with_ignore_empty_lines()
            .with_ignore_surrounding_spaces()
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
        )
        left = right.with_record_separator(Constants.LF)
        assert right != left

    def test_equals_skip_header_record(self):
        right = (
            CSVFormat.new_format("'")
            .with_record_separator(Constants.CR)
            .with_comment_marker("#")
            .with_escape("+")
            .with_ignore_empty_lines()
            .with_ignore_surrounding_spaces()
            .with_quote('"')
            .with_quote_mode(QuoteMode.ALL)
            .with_null_string("null")
            .with_skip_header_record()
        )
        left = right.with_skip_header_record(False)
        assert right != left

    def test_equals_with_null(self):
        csv_format = CSVFormat.POSTGRESQL_TEXT
        assert csv_format.get_escape_character() == '"'
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert not csv_format.get_trim()
        assert csv_format.is_quote_character_set()
        assert csv_format.get_null_string() == "\\N"
        assert not csv_format.get_ignore_header_case()
        assert csv_format.is_escape_character_set()
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_comment_marker() is None
        assert not csv_format.get_allow_missing_column_names()
        assert (
                       csv_format.get_quote_mode()
                       == QuoteMode.ALL_NON_NULL
        )
        assert csv_format.get_delimiter() == "\t"
        assert not csv_format.get_skip_header_record()
        assert csv_format.get_record_separator() == "\n"
        assert not csv_format.get_ignore_empty_lines()
        assert csv_format.get_quote_character() == '"'
        assert csv_format.is_null_string_set()
        assert csv_format.get_escape_character() == '"'
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert not csv_format.get_trim()
        assert csv_format.is_quote_character_set()
        assert csv_format.get_null_string() == "\\N"
        assert not csv_format.get_ignore_header_case()
        assert csv_format.is_escape_character_set()
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_comment_marker() is None
        assert not csv_format.get_allow_missing_column_names()
        assert (
                       csv_format.get_quote_mode()
                       == QuoteMode.ALL_NON_NULL
        )
        assert csv_format.get_delimiter() == "\t"
        assert not csv_format.get_skip_header_record()
        assert csv_format.get_record_separator() == "\n"
        assert not csv_format.get_ignore_empty_lines()
        assert csv_format.get_quote_character() == '"'
        assert csv_format.is_null_string_set()
        assert not csv_format.equals(None)

    def test_escape_same_as_comment_start_raises_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_escape("!").with_comment_marker("!")

    def test_escape_same_as_comment_start_raises_exception_for_wrapper_type(self):
        # Cannot assume that callers won't use different Character objects
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_escape("!").with_comment_marker("!")

    def test_format(self):
        csv_format = CSVFormat.DEFAULT
        assert csv_format.format() == ""
        assert csv_format.format("a", "b", "c") == "a,b,c"
        assert csv_format.format("x,y", "z") == '"x,y",z'

    def test_format_throws_null_pointer_exception(self):
        csv_format = CSVFormat.MYSQL
        try:
            csv_format.format(None)
            pytest.fail("Expected exception: TypeError")
        except TypeError as e:
            assert CSVFormat.__name__ == str(e).split(".")[0]

    def test_get_header(self):
        header = ["one", "two", "three"]
        format_with_header = CSVFormat.DEFAULT.with_header(*header)
        # get_header() makes a copy of the header array.
        header_copy = format_with_header.get_header()
        header_copy[0] = "A"
        header_copy[1] = "B"
        header_copy[2] = "C"
        assert format_with_header.get_header() != header_copy
        assert format_with_header.get_header() is not header_copy

    def test_hash_code_and_with_ignore_header_case(self):
        csv_format = CSVFormat.INFORMIX_UNLOAD_CSV
        csv_format_two = csv_format.with_ignore_header_case()
        csv_format_two.hash_code()
        assert csv_format_two.get_ignore_header_case()
        assert not csv_format_two.get_trailing_delimiter()
        assert csv_format_two.equals(csv_format)
        assert not csv_format_two.get_allow_missing_column_names()
        assert not csv_format_two.get_trim()

    def test_new_format(self):
        csv_format = CSVFormat.new_format("X")
        assert not csv_format.get_skip_header_record()
        assert not csv_format.is_escape_character_set()
        assert csv_format.get_record_separator() is None
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_comment_marker() is None
        assert not csv_format.get_ignore_header_case()
        assert not csv_format.get_allow_missing_column_names()
        assert not csv_format.get_trim()
        assert not csv_format.is_null_string_set()
        assert csv_format.get_escape_character() is None
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert csv_format.get_delimiter() == "X"
        assert csv_format.get_null_string() is None
        assert not csv_format.is_quote_character_set()
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_quote_character() is None
        assert not csv_format.get_ignore_empty_lines()
        assert not csv_format.get_skip_header_record()
        assert not csv_format.is_escape_character_set()
        assert csv_format.get_record_separator() is None
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_comment_marker() is None
        assert not csv_format.get_ignore_header_case()
        assert not csv_format.get_allow_missing_column_names()
        assert not csv_format.get_trim()
        assert not csv_format.is_null_string_set()
        assert csv_format.get_escape_character() is None
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert csv_format.get_delimiter() == "X"
        assert csv_format.get_null_string() is None
        assert not csv_format.is_quote_character_set()
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_quote_character() is None
        assert not csv_format.get_ignore_empty_lines()

    def test_null_record_separator_csv106(self):
        formatter = (
            CSVFormat.new_format(";")
            .with_skip_header_record()
            .with_header("H1", "H2")
        )
        format_str = formatter.format("A", "B")
        assert format_str is not None
        assert not format_str.endswith("null")

    def test_quote_char_same_as_comment_start_raises_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_quote("!").with_comment_marker("!")

    def test_quote_char_same_as_comment_start_raises_exception_for_wrapper_type(self):
        # Cannot assume that callers won't use different Character objects
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_quote("!").with_comment_marker("!")

    def test_quote_char_same_as_delimiter_raises_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_quote("!").with_delimiter("!")

    def test_quote_policy_none_without_escape_raises_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.new_format("!").with_quote_mode(QuoteMode.NONE)

    def test_rfc4180(self):
        csv_format = CSVFormat.RFC4180
        assert csv_format.get_comment_marker() is None
        assert csv_format.get_delimiter() == ","
        assert csv_format.get_escape_character() is None
        assert not csv_format.get_ignore_empty_lines()
        assert csv_format.get_quote_character() == '"'
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_record_separator() == "\r\n"

    def test_serialization(self):
        out = BytesIO()
        pickle.dump(CSVFormat.DEFAULT, out)
        out.seek(0)
        
        inp = BytesIO(out.read())
        formatter = pickle.load(inp)
        csv_format = CSVFormat.DEFAULT
        assert formatter is not None
        assert csv_format.get_delimiter() == formatter.get_delimiter()
        assert (
            csv_format.get_quote_character()
            == formatter.get_quote_character()
        )
        assert (
            csv_format.get_comment_marker()
            == formatter.get_comment_marker()
        )
        assert (
            csv_format.get_record_separator()
            == formatter.get_record_separator()
        )
        assert (
            csv_format.get_escape_character()
            == formatter.get_escape_character()
        )
        assert (
            csv_format.get_ignore_surrounding_spaces()
            == formatter.get_ignore_surrounding_spaces()
        )
        assert (
            csv_format.get_ignore_empty_lines()
            == formatter.get_ignore_empty_lines()
        )

    def test_to_string(self):
        # csv_format = CSVFormat.POSTGRESQL_TEXT
        string = CSVFormat.INFORMIX_UNLOAD.to_string()
        assert (
            string
            == 'Delimiter=<|> Escape=<\\> QuoteChar=<"> '
            'RecordSeparator=<\n> EmptyLines:ignored SkipHeaderRecord:false'
        )

    def test_to_string_and_with_comment_marker_taking_character(self):
        csv_format_predefined = CSVFormat.Predefined.Default
        csv_format = csv_format_predefined.get_format()
        assert csv_format.get_escape_character() is None
        assert csv_format.is_quote_character_set()
        assert not csv_format.get_trim()
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert csv_format.get_delimiter() == ","
        assert not csv_format.get_ignore_header_case()
        assert csv_format.get_record_separator() == "\r\n"
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_comment_marker() is None
        assert not csv_format.is_null_string_set()
        assert not csv_format.get_allow_missing_column_names()
        assert not csv_format.is_escape_character_set()
        assert not csv_format.get_skip_header_record()
        assert csv_format.get_null_string() is None
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_ignore_empty_lines()
        assert csv_format.get_quote_character() == '"'
        assert csv_format.get_escape_character() is None
        assert csv_format.is_quote_character_set()
        assert not csv_format.get_trim()
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert csv_format.get_delimiter() == ","
        assert not csv_format.get_ignore_header_case()
        assert csv_format.get_record_separator() == "\r\n"
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_comment_marker() is None
        assert not csv_format.is_null_string_set()
        assert not csv_format.get_allow_missing_column_names()
        assert not csv_format.is_escape_character_set()
        assert not csv_format.get_skip_header_record()
        assert csv_format.get_null_string() is None
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_ignore_empty_lines()
        assert csv_format.get_quote_character() == '"'
        csv_format_two = csv_format.with_comment_marker("n")
        assert not csv_format_two.is_null_string_set()
        assert not csv_format_two.get_allow_missing_column_names()
        assert csv_format_two.get_quote_character() == '"'
        assert csv_format_two.get_null_string() is None
        assert csv_format_two.get_delimiter() == ","
        assert not csv_format_two.get_trailing_delimiter()
        assert csv_format_two.is_comment_marker_set()
        assert not csv_format_two.get_ignore_header_case()
        assert not csv_format_two.get_trim()
        assert csv_format_two.get_escape_character() is None
        assert csv_format_two.is_quote_character_set()
        assert not csv_format_two.get_ignore_surrounding_spaces()
        assert csv_format_two.get_record_separator() == "\r\n"
        assert csv_format_two.get_quote_mode() is None
        assert csv_format_two.get_comment_marker() == "n"
        assert not csv_format_two.get_skip_header_record()
        assert not csv_format_two.is_escape_character_set()
        assert csv_format_two.get_ignore_empty_lines()
        assert csv_format != csv_format_two
        assert csv_format_two != csv_format
        assert not csv_format_two.equals(csv_format)
        assert csv_format.get_escape_character() is None
        assert csv_format.is_quote_character_set()
        assert not csv_format.get_trim()
        assert not csv_format.get_ignore_surrounding_spaces()
        assert not csv_format.get_trailing_delimiter()
        assert csv_format.get_delimiter() == ","
        assert not csv_format.get_ignore_header_case()
        assert csv_format.get_record_separator() == "\r\n"
        assert not csv_format.is_comment_marker_set()
        assert csv_format.get_comment_marker() is None
        assert not csv_format.is_null_string_set()
        assert not csv_format.get_allow_missing_column_names()
        assert not csv_format.is_escape_character_set()
        assert not csv_format.get_skip_header_record()
        assert csv_format.get_null_string() is None
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_ignore_empty_lines()
        assert csv_format.get_quote_character() == '"'
        assert not csv_format_two.is_null_string_set()
        assert not csv_format_two.get_allow_missing_column_names()
        assert csv_format_two.get_quote_character() == '"'
        assert csv_format_two.get_null_string() is None
        assert csv_format_two.get_delimiter() == ","
        assert not csv_format_two.get_trailing_delimiter()
        assert csv_format_two.is_comment_marker_set()
        assert not csv_format_two.get_ignore_header_case()
        assert not csv_format_two.get_trim()
        assert csv_format_two.get_escape_character() is None
        assert csv_format_two.is_quote_character_set()
        assert not csv_format_two.get_ignore_surrounding_spaces()
        assert csv_format_two.get_record_separator() == "\r\n"
        assert csv_format_two.get_quote_mode() is None
        assert csv_format_two.get_comment_marker() == "n"
        assert not csv_format_two.get_skip_header_record()
        assert not csv_format_two.is_escape_character_set()
        assert csv_format_two.get_ignore_empty_lines()
        assert csv_format != csv_format_two
        assert csv_format_two != csv_format
        assert not csv_format_two.equals(csv_format)
        assert (
            csv_format_two.to_string()
            == 'Delimiter=<,> QuoteChar=<"> CommentStart=<n> '
            "RecordSeparator=<\r\n> "
            "EmptyLines:ignored SkipHeaderRecord:false"
        )

    def test_with_comment_start(self):
        format_with_comment_start = CSVFormat.DEFAULT \
            .with_comment_marker("#")
        assert format_with_comment_start.get_comment_marker() == "#"

    def test_with_comment_start_CR_raises_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_comment_marker("\r")

    def test_with_delimiter(self):
        format_with_delimiter = CSVFormat.DEFAULT \
            .with_delimiter("!")
        assert format_with_delimiter.get_delimiter() == "!"

    def test_with_delimiter_lf_raises_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_delimiter("\n")

    def test_with_empty_enum(self):
        format_with_header = CSVFormat.DEFAULT.with_header(Enum('EmptyEnum', []))
        assert len(format_with_header.get_header()) == 0

    def test_with_escape(self):
        format_with_escape = CSVFormat.DEFAULT.with_escape("&")
        assert format_with_escape.get_escape_character() == "&"

    def test_with_escape_cr_raises_exceptions(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_escape("\r")

    def test_with_first_record_as_header(self):
        format_with_first_record_as_header = (
            CSVFormat.DEFAULT.with_skip_header_record().with_header()
        )
        assert (format_with_first_record_as_header.
                get_skip_header_record()
                )
        assert len(format_with_first_record_as_header.
                   get_header()) == 0

    def test_with_header(self):
        header = ["one", "two", "three"]
        format_with_header = (CSVFormat.DEFAULT
                              .with_header(*header)
                              )
        assert format_with_header.get_header() == header
        assert format_with_header.get_header() is not header

    def test_with_header_comments(self):
        csv_format = CSVFormat.DEFAULT
        assert csv_format.get_quote_character() == '"'
        assert not csv_format.is_comment_marker_set()
        assert not csv_format.is_escape_character_set()
        assert csv_format.is_quote_character_set()
        assert not csv_format.get_skip_header_record()
        assert csv_format.get_quote_mode() is None
        assert csv_format.get_delimiter() == ","
        assert csv_format.get_ignore_empty_lines()
        assert not csv_format.get_ignore_header_case()
        assert csv_format.get_comment_marker() is None
        assert csv_format.get_record_separator() == "\r\n"
        assert not csv_format.get_trailing_delimiter()
        assert not csv_format.get_allow_missing_column_names()
        assert not csv_format.get_trim()
        assert not csv_format.is_null_string_set()
        assert csv_format.get_null_string() is None
        assert not csv_format.get_ignore_surrounding_spaces()
        assert csv_format.get_escape_character() is None
        object_array = [None] * 8
        csv_format_two = csv_format.with_header_comments(object_array)
        assert not csv_format_two.get_ignore_header_case()
        assert csv_format_two.get_quote_mode() is None
        assert csv_format_two.get_ignore_empty_lines()
        assert not csv_format_two.get_ignore_surrounding_spaces()
        assert csv_format_two.get_escape_character() is None
        assert not csv_format_two.get_trim()
        assert not csv_format_two.is_escape_character_set()
        assert csv_format_two.is_quote_character_set()
        assert not csv_format_two.get_skip_header_record()
        assert csv_format_two.get_quote_character() == '"'
        assert not csv_format_two.get_allow_missing_column_names()
        assert csv_format_two.get_null_string() is None
        assert not csv_format_two.is_null_string_set()
        assert not csv_format_two.get_trailing_delimiter()
        assert csv_format_two.get_record_separator() == "\r\n"
        assert csv_format_two.get_delimiter() == ","
        assert csv_format_two.get_comment_marker() is None
        assert not csv_format_two.is_comment_marker_set()
        assert csv_format is not csv_format_two
        assert csv_format_two is not csv_format
        assert csv_format_two.equals(csv_format)
        string = csv_format_two.format(*object_array)
        assert not csv_format_two.get_ignore_header_case()
        assert csv_format_two.get_quote_mode() is None
        assert csv_format_two.get_ignore_empty_lines()
        assert not csv_format_two.get_ignore_surrounding_spaces()
        assert csv_format_two.get_escape_character() is None
        assert not csv_format_two.get_trim()
        assert not csv_format_two.is_escape_character_set()
        assert csv_format_two.is_quote_character_set()
        assert not csv_format_two.get_skip_header_record()
        assert csv_format_two.get_quote_character() == '"'
        assert not csv_format_two.get_allow_missing_column_names()
        assert csv_format_two.get_null_string() is None
        assert not csv_format_two.is_null_string_set()
        assert not csv_format_two.get_trailing_delimiter()
        assert csv_format_two.get_record_separator() == "\r\n"
        assert csv_format_two.get_delimiter() == ","
        assert csv_format_two.get_comment_marker() is None
        assert not csv_format_two.is_comment_marker_set()
        assert csv_format is not csv_format_two
        assert csv_format_two is not csv_format
        assert string is not None
        assert csv_format_two.equals(csv_format)
        assert string == ",,,,,,,"

    def test_with_header_enum(self):
        format_with_header = (CSVFormat.DEFAULT
                              .with_header(TestCSVFormat.Header)
                              )
        expected_header = ["Name", "Email", "Phone"]
        assert list(format_with_header.get_header()) == expected_header

    def test_with_ignore_empty_lines(self):
        assert not (CSVFormat.DEFAULT
                    .with_ignore_empty_lines(False)
                    .get_ignore_empty_lines()
                    )
        assert (CSVFormat.DEFAULT
                .with_ignore_empty_lines()
                .get_ignore_empty_lines()
                )

    def test_with_ignore_surround(self):
        assert not (CSVFormat.DEFAULT
                    .with_ignore_surrounding_spaces(False)
                    .get_ignore_surrounding_spaces()
                    )
        assert (
            CSVFormat.DEFAULT
            .with_ignore_surrounding_spaces()
            .get_ignore_surrounding_spaces()
        )

    def test_with_null_string(self):
        format_with_null_string = (CSVFormat.DEFAULT
                                   .with_null_string("null")
                                   )
        assert format_with_null_string.get_null_string() == "null"

    def test_with_quote_char(self):
        format_with_quote_char = CSVFormat.DEFAULT.with_quote('"')
        assert format_with_quote_char.get_quote_character() == '"'

    def test_with_quote_lf_throws_exception(self):
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_quote("\n")

    def test_with_quote_policy(self):
        format_with_quote_policy = (CSVFormat.DEFAULT
                                    .with_quote_mode(QuoteMode.ALL)
                                    )
        assert format_with_quote_policy.get_quote_mode() == QuoteMode.ALL

    def test_with_record_separator_cr(self):
        format_with_record_separator = (CSVFormat.DEFAULT
                                        .with_record_separator(Constants.CR)
                                        )
        assert format_with_record_separator.get_record_separator() == "\r"

    def test_with_record_separator_crlf(self):
        format_with_record_separator = (CSVFormat.DEFAULT
                                        .with_record_separator(Constants.CRLF)
                                        )
        assert (
                format_with_record_separator
                .get_record_separator() == "\r\n"
        )

    def test_with_record_separator_lf(self):
        format_with_record_separator = (CSVFormat.DEFAULT
                                        .with_record_separator(Constants.LF)
                                        )
        assert (
                format_with_record_separator
                .get_record_separator() == "\n"
        )

    def test_with_system_record_separator(self):
        format_with_record_separator = (CSVFormat.DEFAULT
                                        .with_system_record_separator()
                                        )
        assert (
                format_with_record_separator
                .get_record_separator()
                == os.linesep
        )
