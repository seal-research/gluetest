from enum import Enum
import sys
import os
import io
import sqlite3
from main.python.csv_printer import CSVPrinter
from main.python.csv_parser import CSVParser
from main.python.quote_mode import QuoteMode
from main.python.constants import Constants
from main.python.java_handler import Types, convert_to_python_enum, java_handler

@java_handler
class CSVFormat:

    class Predefined:
        def __init__(self, formatter):
            self.format = formatter

        def get_format(self):
            return self.format
        
        @staticmethod
        def value_of(name):
            return getattr(CSVFormat.Predefined, name)

    def __init__(
        self,
        delimiter: str,
        quote_char: str,
        quote_mode: QuoteMode,
        comment_start: str,
        escape: str,
        ignore_surrounding_spaces: bool,
        ignore_empty_lines: bool,
        record_separator: str,
        null_string: str,
        header_comments: list[object],
        header: list[str],
        skip_header_record: bool,
        allow_missing_column_names: bool,
        ignore_header_case: bool,
        trim: bool,
        trailing_delimiter: bool,
        auto_flush: bool,
    ):
        self.delimiter = delimiter
        self.quote_character = quote_char
        self.quote_mode = quote_mode
        self.comment_marker = comment_start
        self.escape_character = escape
        self.ignore_surrounding_spaces = ignore_surrounding_spaces
        self.ignore_empty_lines = ignore_empty_lines
        self.record_separator = record_separator
        self.null_string = null_string
        self.header_comments = self.__convert_header_comments(header_comments) if header_comments else []
        self.header = list(header) if header is not None else None
        self.skip_header_record = skip_header_record
        self.allow_missing_column_names = allow_missing_column_names
        self.ignore_header_case = ignore_header_case
        self.trailing_delimiter = trailing_delimiter
        self.trim = trim
        self.auto_flush = auto_flush
        self.validate()

    @staticmethod
    def is_line_break(c: str):
        return c in {Constants.LF, Constants.CR}

    @staticmethod
    def new_format(delimiter: str):
        return CSVFormat(
            delimiter,
            None,
            None,
            None,
            None,
            False,
            False,
            None,
            None,
            None,
            None,
            False,
            False,
            False,
            False,
            False,
            False,
        )

    @staticmethod
    def value_of(format: str):
        return CSVFormat.Predefined.value_of(format).get_format()

    # ensure all header comments are strings
    def __convert_header_comments(self, header_comments):
        # return [str(comment) for comment in header_comments]
        comments = []
        for comment in header_comments:
            if hasattr(comment, "toString"):
                comments.append(comment.toString())
            else:
                comments.append(str(comment))
        return comments

    def __eq__(self, other: object):
        if self is other:
            return True
        if not isinstance(other, CSVFormat):
            return False

        return (
            self.delimiter == other.delimiter
            and self.quote_mode == other.quote_mode
            and self.quote_character == other.quote_character
            and self.comment_marker == other.comment_marker
            and self.escape_character == other.escape_character
            and self.null_string == other.null_string
            and self.header == other.header
            and (self.ignore_surrounding_spaces
                 == other.ignore_surrounding_spaces
                 )
            and self.ignore_empty_lines == other.ignore_empty_lines
            and self.skip_header_record == other.skip_header_record
            and self.record_separator == other.record_separator
        )

    def equals(self, other: object):
        return self == other

    def format(self, *values):
        """
        Formats the specified values.
        :values: the values to format
        :return: the formatted values
        """
        out = io.StringIO()
        csv_printer = CSVPrinter(out, self)
        csv_printer.print_record(*values)
        return out.getvalue().strip()

    def get_allow_missing_column_names(self):
        return self.allow_missing_column_names

    def get_auto_flush(self):
        return self.auto_flush

    def get_comment_marker(self):
        return self.comment_marker

    def get_delimiter(self):
        return self.delimiter

    def get_escape_character(self):
        return self.escape_character

    def get_header(self):
        if hasattr(self.header, "copy"):
                    return self.header.copy()
        if hasattr(self.header, "clone"):
            # header is a java list
            return self.header.clone()
        return None

    def get_header_comments(self):
        return self.header_comments.copy() \
            if hasattr(self.header_comments, "copy") \
            else self.header_comments

    def get_ignore_empty_lines(self):
        return self.ignore_empty_lines

    def get_ignore_header_case(self):
        return self.ignore_header_case

    def get_ignore_surrounding_spaces(self):
        return self.ignore_surrounding_spaces

    def get_null_string(self):
        return self.null_string

    def get_quote_character(self):
        return self.quote_character

    def get_quote_mode(self):
        return self.quote_mode

    def get_record_separator(self):
        return self.record_separator

    def get_skip_header_record(self):
        return self.skip_header_record

    def get_trailing_delimiter(self):
        return self.trailing_delimiter

    def get_trim(self):
        return self.trim

    def __hash__(self):
        prime = 31
        result = 1

        result = prime * result + hash(self.delimiter)
        result = prime * result + (
            hash(self.quote_mode) if self.quote_mode else 0
        )
        result = prime * result + (
            hash(self.quote_character) if self.quote_character else 0
        )
        result = prime * result + (
            hash(self.comment_marker) if self.comment_marker else 0
        )
        result = prime * result + (
            hash(self.escape_character) if self.escape_character else 0
        )
        result = prime * result + \
            (hash(self.null_string) if self.null_string else 0)
        result = prime * result + hash(self.ignore_surrounding_spaces)
        result = prime * result + hash(self.ignore_empty_lines)
        result = prime * result + hash(self.skip_header_record)
        result = prime * result + (
            hash(self.record_separator) if self.record_separator else 0
        )
        result = prime * result + \
            hash(tuple(self.header) if self.header else ())
        return result

    def hash_code(self):
        return hash(self)

    def is_comment_marker_set(self):
        return self.comment_marker != None

    def is_escape_character_set(self):
        return self.escape_character != None

    def is_null_string_set(self):
        return self.null_string != None

    def is_quote_character_set(self):
        return self.quote_character != None

    def parse(self, in_reader):
        return CSVParser(in_reader, self)
    
    # add support for file-like objects (e.g. sys.stdout)
    def _append(self, appendable, string):
        if hasattr(appendable, "append"):
            try: appendable.append(string)
            except: appendable.append(string.encode("utf-8"))
        else:
            try: appendable.write(string)
            except: appendable.write(string.encode("utf-8"))

    def print(self, *args):
        if len(args) == 1:
            return self._print(*args)
        if len(args) == 2:
            return self._print_file(*args)
        if len(args) == 3:
            return self._print_to_appendable(*args)
        if len(args) == 6:
            return self._print_object(*args)
        raise ValueError()
        

    def _print(self, out):
        return CSVPrinter(out, self)

    def _print_file(self, out_file, charset):
        if isinstance(out_file, io.TextIOWrapper):
            return CSVPrinter(out_file, self)
        return CSVPrinter(io.open(out_file, mode="w", encoding=charset), self)

    def _print_to_appendable(self, value, out, new_record: bool):
        char_sequence = Constants.EMPTY
        quote_mode_policy = self.quote_mode
        if value is None:
            if self.null_string == None:
                char_sequence = Constants.EMPTY
            else:
                if quote_mode_policy != None and isinstance(quote_mode_policy, Types.Enum):
                    quote_mode_policy = convert_to_python_enum(quote_mode_policy, QuoteMode)

                if quote_mode_policy == QuoteMode.ALL:
                    char_sequence = (
                        self.quote_character +
                        self.null_string +
                        self.quote_character
                    )
                else:
                    char_sequence = self.null_string
        else:
            char_sequence = str(value) if not isinstance(value, str) else value
        char_sequence = char_sequence.strip() if self.trim else char_sequence
        self.print(value, char_sequence, 0, len(
            char_sequence), out, new_record)

    def _print_object(self, obj, value, offset: int, length: int, out, new_record: bool):
        if not new_record:
            self._append(out, self.delimiter)
        if obj is None:
            # convert value to bytes for compatibility with java if it fails
            self._append(out,value)
        elif self.is_quote_character_set():
            self.print_and_quote(obj, value, offset, length, out, new_record)
        elif self.is_escape_character_set():
            self.print_and_escape(value, offset, length, out)
        else:
            self._append(out, value[offset:offset + length])

    def print_and_escape(self, value, offset: int, length: int, out):
        start = offset
        pos = offset
        end = offset + length

        delim = self.get_delimiter()
        escape = self.escape_character
        while pos < end:
            c = value[pos]
            if c in {Constants.CR, Constants.LF, delim, escape}:
                if pos > start:
                    self._append(out, value[start:pos])
                if c == Constants.LF:
                    c = "n"
                elif c == Constants.CR:
                    c = "r"
                self._append(out, escape)
                self._append(out, c)
                start = pos + 1
            pos += 1

        if pos > start:
            self._append(out, value[start:pos])

    def print_and_quote(
            self, obj, value, offset: int, length: int, out, new_record: bool
    ):
        quote = False
        start = offset
        pos = offset
        end = offset + length

        delim_char = self.get_delimiter()
        quote_char = self.quote_character

        quote_mode_policy = (
            self.get_quote_mode()
            if self.quote_mode != None
            else QuoteMode.MINIMAL
        )
        
        if isinstance(quote_mode_policy, Types.Enum):
            quote_mode_policy = convert_to_python_enum(quote_mode_policy, QuoteMode)

        if quote_mode_policy in [QuoteMode.ALL, QuoteMode.ALL_NON_NULL]:
            quote = True
        elif quote_mode_policy == QuoteMode.NON_NUMERIC:
            quote = not isinstance(obj, (int, float))
        elif quote_mode_policy == QuoteMode.NONE:
            self.print_and_escape(value, offset, length, out)
            return
        elif quote_mode_policy == QuoteMode.MINIMAL:
            if length <= 0:
                if new_record:
                    quote = True
            else:
                c = value[pos]
                if ord(c) <= ord(Constants.COMMENT):
                    quote = True
                else:
                    while pos < end:
                        c = value[pos]
                        if (c == Constants.LF or c == Constants.CR
                                or c == quote_char or c == delim_char):
                            quote = True
                            break
                        pos += 1

                    if not quote:
                        pos = end - 1
                        c = value[pos]

                        if ord(c) <= ord(Constants.SP):
                            quote = True

            if not quote:
                self._append(out, value[start:end])
                return
        else:
            raise ValueError("Unexpected Quote value: " + quote_mode_policy)

        if not quote:
            self._append(out, value[start:end])
            return

        self._append(out, quote_char)

        while pos < end:
            c = value[pos]
            if c == quote_char:
                self._append(out, value[start: pos + 1])
                start = pos
            pos += 1

        self._append(out, value[start:end])
        self._append(out, quote_char)
        
    def printer(self):
        return CSVPrinter(sys.stdout, self)

    def println(self, out):
        if self.get_trailing_delimiter():
            try:
                self._append(out, self.get_delimiter())
            except:
                self._append(out, self.get_delimiter().encode("utf-8"))
        if self.record_separator:
            try:
                self._append(out, self.record_separator)
            except:
                self._append(out, self.record_separator.encode("utf-8"))

    def print_record(self, out, *values):
        if values == (None,):
            raise TypeError("CSVFormat.print_record")

        for i, value in enumerate(values):
            self.print(value, out, i == 0)
        self.println(out)

    def __str__(self):
        sb = []
        sb.append(f"Delimiter=<{self.delimiter}>")
        if self.is_escape_character_set():
            sb.append(f" Escape=<{self.escape_character}>")
        if self.is_quote_character_set():
            sb.append(f" QuoteChar=<{self.quote_character}>")
        if self.is_comment_marker_set():
            sb.append(f" CommentStart=<{self.comment_marker}>")
        if self.is_null_string_set():
            sb.append(f" NullString=<{self.null_string}>")
        if self.record_separator:
            sb.append(f" RecordSeparator=<{self.record_separator}>")
        if self.get_ignore_empty_lines():
            sb.append(" EmptyLines:ignored")
        if self.get_ignore_surrounding_spaces():
            sb.append(" SurroundingSpaces:ignored")
        if self.get_ignore_header_case():
            sb.append(" IgnoreHeaderCase:ignored")
        sb.append(f" SkipHeaderRecord:{str(self.get_skip_header_record()).lower()}")
        if self.header_comments:
            sb.append(f" HeaderComments:{self.header_comments}")
        if self.header:
            sb.append(f" Header:{self.header}")
        return "".join(sb)

    def to_string(self):
        return str(self)

    def to_string_array(self, *values):
        if values is None:
            return None
        strings = [None] * len(values)
        for i, value in enumerate(values):
            strings[i] = str(value) if value is not None else None
        return strings

    # unused method
    def __trim(self, char_sequence):
        if isinstance(char_sequence, str):
            return char_sequence.strip()
        count = len(char_sequence)
        length = count
        pos = 0
        while pos < length and char_sequence[pos] <= Constants.SP:
            pos += 1
        while pos < length and char_sequence[length - 1] <= Constants.SP:
            length -= 1
        if pos > 0 or length < count:
            return char_sequence[pos:length]
        return char_sequence

    def validate(self):
        if self.is_line_break(self.delimiter):
            raise ValueError("The delimiter cannot be a line break")

        if (self.quote_character != None
                and self.delimiter == self.quote_character):
            raise ValueError(
                f"The quoteChar character and the delimiter"
                f" cannot be the same ('{self.quote_character}')"
            )

        if (
            self.escape_character != None
            and self.delimiter == self.escape_character
        ):
            raise ValueError(
                f"The escape character and the delimiter"
                f" cannot be the same ('{self.escape_character}')"
            )

        if (self.comment_marker != None
                and self.delimiter == self.comment_marker):
            raise ValueError(
                f"The comment start character and the "
                f"delimiter cannot be the same ('{self.comment_marker}')"
            )

        if (
            self.quote_character != None
            and self.quote_character == self.comment_marker
        ):
            raise ValueError(
                f"The comment start character and the "
                f"quoteChar cannot be the same ('{self.comment_marker}')"
            )

        if (
            self.escape_character != None
            and self.escape_character == self.comment_marker
        ):
            raise ValueError(
                f"The comment start and the escape "
                f"character cannot be the same ('{self.comment_marker}')"
            )

        quote_mode_policy = self.quote_mode
        if self.quote_mode and isinstance(quote_mode_policy, Types.Enum):
                quote_mode_policy = convert_to_python_enum(quote_mode_policy, QuoteMode)

        if self.escape_character == None and quote_mode_policy == QuoteMode.NONE:
            raise ValueError(
                "No quotes mode set but no escape character is set")

        if self.header:
            duplicate_check = set()
            for hdr in self.header:
                if hdr in duplicate_check:
                    raise ValueError(
                        f"The header contains a duplicate entry:"
                        f" '{hdr}' in {self.header}"
                    )
                duplicate_check.add(hdr)

    def with_allow_missing_column_names(
            self, allow_missing_column_names=True
    ):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_auto_flush(self, auto_flush):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            auto_flush,
        )

    def with_comment_marker(self, comment_marker: str):
        if self.is_line_break(comment_marker):
            raise ValueError(
                "The comment start marker character cannot be a line break"
            )
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_delimiter(self, delimiter: str):
        if self.is_line_break(delimiter):
            raise ValueError("The delimiter cannot be a line break")
        return CSVFormat(
            delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_escape(self, escape: str):
        if self.is_line_break(escape):
            raise ValueError("The escape character cannot be a line break")
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            escape,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_first_record_as_header(self):
        return self.with_header().with_skip_header_record()
    
    def with_header(self, *args):        
        if len(args) == 1 and isinstance(args[0], type(Enum)):
            return self._with_header_from_enum(args[0])
        if len(args) == 1 and isinstance(args[0], sqlite3.Cursor):
            return self._with_header_from_result_set(args[0])
        return self._with_header(*args)

    def _with_header_from_enum(self, header_enum: Enum):
        header = (
            [enum_value.name for enum_value in header_enum]
            if header_enum is not None
            else None
        )
        return self.with_header(*header)
    
    def _with_header_from_result_set(self, result_set):
        labels = []
        for res in result_set.description:
            labels.append(res[0])
        return self.with_header(*labels)

    def _with_header(self, *header):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_header_comments(self, *header_comments):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_ignore_empty_lines(self, ignore_empty_lines: bool = True):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_ignore_header_case(self, ignore_header_case: bool = True):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_ignore_surrounding_spaces(
            self, ignore_surrounding_spaces: bool = True
            ):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_null_string(self, null_string: str):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_quote(self, quote_char: str):
        if self.is_line_break(quote_char):
            raise ValueError("The quoteChar cannot be a line break")
        return CSVFormat(
            self.delimiter,
            quote_char,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_quote_mode(self, quote_mode_policy: QuoteMode):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            quote_mode_policy,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush
        )

    def with_record_separator(self, record_separator: str):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_skip_header_record(self, skip_header_record: bool = True):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            self.trailing_delimiter,
            self.auto_flush,
        )

    def with_system_record_separator(self):
        return self.with_record_separator(os.linesep)

    def with_trailing_delimiter(self, trailing_delimiter: bool = True):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            self.trim,
            trailing_delimiter,
            self.auto_flush,
        )

    def with_trim(self, trim: bool = True):
        return CSVFormat(
            self.delimiter,
            self.quote_character,
            self.quote_mode,
            self.comment_marker,
            self.escape_character,
            self.ignore_surrounding_spaces,
            self.ignore_empty_lines,
            self.record_separator,
            self.null_string,
            self.header_comments,
            self.header,
            self.skip_header_record,
            self.allow_missing_column_names,
            self.ignore_header_case,
            trim,
            self.trailing_delimiter,
            self.auto_flush,
        )


CSVFormat.DEFAULT = CSVFormat(
    Constants.COMMA,
    Constants.DOUBLE_QUOTE_CHAR,
    None,
    None,
    None,
    False,
    True,
    Constants.CRLF,
    None,
    None,
    None,
    False,
    False,
    False,
    False,
    False,
    False,
)

CSVFormat.EXCEL = (
    CSVFormat.DEFAULT.with_ignore_empty_lines(False)
    .with_allow_missing_column_names()
)

CSVFormat.INFORMIX_UNLOAD = (
    CSVFormat.DEFAULT.with_delimiter(Constants.PIPE)
    .with_escape(Constants.BACKSLASH)
    .with_quote(Constants.DOUBLE_QUOTE_CHAR)
    .with_record_separator(Constants.LF)
)

CSVFormat.INFORMIX_UNLOAD_CSV = (
    CSVFormat.DEFAULT.with_delimiter(Constants.COMMA)
    .with_quote(Constants.DOUBLE_QUOTE_CHAR)
    .with_record_separator(Constants.LF)
)

CSVFormat.MYSQL = (
    CSVFormat.DEFAULT.with_delimiter(Constants.TAB)
    .with_escape(Constants.BACKSLASH)
    .with_ignore_empty_lines(False)
    .with_quote(None)
    .with_record_separator(Constants.LF)
    .with_null_string(Constants.SQL_NULL_STRING)
    .with_quote_mode(QuoteMode.ALL_NON_NULL)
)

CSVFormat.ORACLE = (
    CSVFormat.DEFAULT.with_delimiter(Constants.COMMA)
    .with_escape(Constants.BACKSLASH)
    .with_ignore_empty_lines(False)
    .with_quote(Constants.DOUBLE_QUOTE_CHAR)
    .with_null_string(Constants.SQL_NULL_STRING)
    .with_trim()
    .with_system_record_separator()
    .with_quote_mode(QuoteMode.MINIMAL)
)

CSVFormat.POSTGRESQL_CSV = (
    CSVFormat.DEFAULT.with_delimiter(Constants.COMMA)
    .with_escape(Constants.DOUBLE_QUOTE_CHAR)
    .with_ignore_empty_lines(False)
    .with_quote(Constants.DOUBLE_QUOTE_CHAR)
    .with_record_separator(Constants.LF)
    .with_null_string(Constants.EMPTY)
    .with_quote_mode(QuoteMode.ALL_NON_NULL)
)

CSVFormat.POSTGRESQL_TEXT = (
    CSVFormat.DEFAULT.with_delimiter(Constants.TAB)
    .with_escape(Constants.DOUBLE_QUOTE_CHAR)
    .with_ignore_empty_lines(False)
    .with_quote(Constants.DOUBLE_QUOTE_CHAR)
    .with_record_separator(Constants.LF)
    .with_null_string(Constants.SQL_NULL_STRING)
    .with_quote_mode(QuoteMode.ALL_NON_NULL)
)

CSVFormat.RFC4180 = CSVFormat.DEFAULT.with_ignore_empty_lines(False)

CSVFormat.TDF = (
    CSVFormat.DEFAULT.
    with_delimiter(Constants.TAB).
    with_ignore_surrounding_spaces()
)


CSVFormat.Predefined.Default = CSVFormat.Predefined(CSVFormat.DEFAULT)
CSVFormat.Predefined.Excel = CSVFormat.Predefined(CSVFormat.EXCEL)
CSVFormat.Predefined.InformixUnload = CSVFormat.Predefined(CSVFormat.INFORMIX_UNLOAD)
CSVFormat.Predefined.InformixUnloadCsv = CSVFormat.Predefined(CSVFormat.INFORMIX_UNLOAD_CSV)
CSVFormat.Predefined.MySQL = CSVFormat.Predefined(CSVFormat.MYSQL)
CSVFormat.Predefined.Oracle = CSVFormat.Predefined(CSVFormat.ORACLE)
CSVFormat.Predefined.PostgreSQLCsv = CSVFormat.Predefined(CSVFormat.POSTGRESQL_CSV)
CSVFormat.Predefined.PostgreSQLText = CSVFormat.Predefined(CSVFormat.POSTGRESQL_TEXT)
CSVFormat.Predefined.RFC4180 = CSVFormat.Predefined(CSVFormat.RFC4180)
CSVFormat.Predefined.TDF = CSVFormat.Predefined(CSVFormat.TDF)
