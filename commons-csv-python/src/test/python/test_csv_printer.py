import locale
import os
from pathlib import Path
import sys
import pytest
import random
import string
import io
import sqlite3
from datetime import datetime
from main.python.csv_format import CSVFormat
from main.python.csv_printer import CSVPrinter
from main.python.csv_parser import CSVParser
from main.python.quote_mode import QuoteMode
from main.python.string_writer import StringWriter
from test.python.utils import Utils
from tempfile import NamedTemporaryFile
from unittest.mock import Mock


class TestCSVPrinter:

    EURO_CH = '\u20AC'
    DQUOTE_CHAR = '"'
    BACKSLASH_CH = '\\'
    QUOTE_CH = '\''
    ITERATIONS_FOR_RANDOM_TEST = 5000

    @staticmethod
    def printable(s):
        return ''.join(
            f'({ord(ch)})' if ch <= ' ' or ord(ch) >= 128 else ch
            for ch in s
        )

    record_separator = CSVFormat.DEFAULT.get_record_separator()

    def do_one_random(self, format):
        r = random.Random()

        n_lines = r.randint(1, 4)
        n_col = r.randint(1, 3)
        lines = self.generate_lines(n_lines, n_col)

        sw = StringWriter()
        with CSVPrinter(sw, format=format) as printer:
            for i in range(n_lines):
                printer.print_record(*lines[i])
            printer.flush()

        result = sw.getvalue()

        with CSVParser.parse(result, format) as parser:
            parse_result = parser.get_records()
            expected = lines.copy()
            for i in range(len(expected)):
                expected[i] = self.expect_nulls(expected[i], format)
            Utils.compare(
                f'Printer output: {self.printable(result)}',
                expected, parse_result
            )

    def do_random(self, format, iter):
        for _ in range(iter):
            self.do_one_random(format)

    @staticmethod
    def expect_nulls(original, CSVFormat):
        return [
            None if obj == CSVFormat.get_null_string() else obj
            for obj in original
        ]

    def ge_h2_connection(self):
        conn = sqlite3.connect(':memory:')
        return conn

    @staticmethod
    def generate_lines(n_lines, n_col):
        lines = []
        for _ in range(n_lines):
            line = [TestCSVPrinter.rand_str() for _ in range(n_col)]
            lines.append(line)
        return lines

    @staticmethod
    def print_with_header_comments(sw, now, base_format):
        format = base_format
        format = format.with_header_comments(
            "Generated by Apache Commons CSV 1.1", str(now)
        )
        format = format.with_comment_marker('#')
        format = format.with_header("Col1", "Col2")
        csv_printer = format.print(sw)
        csv_printer.print_record("A", "B")
        csv_printer.print_record("C", "D")
        csv_printer.close()
        return csv_printer

    @staticmethod
    def rand_str():
        sz = random.randint(1, 20)
        allowed_chars = (
            string.ascii_letters + string.digits +
            string.punctuation + ' '
        )
        buf = [random.choice(allowed_chars) for _ in range(sz)]
        return ''.join(buf)

    def set_up_table(self, connection):
        cursor = connection.cursor()
        cursor.execute(
            "CREATE TABLE TEST(ID INTEGER PRIMARY KEY, NAME VARCHAR(255))"
        )
        cursor.executemany(
            "INSERT INTO TEST VALUES (?, ?)", [(1, 'r1'), (2, 'r2')]
        )
        
    def to_first_record_values(self, expected, format):
        return CSVParser.parse(expected, format).get_records()[0].values()

    def test_delimeter_quoted(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_quote('\'')) as printer:
            printer.print("a,b,c")
            printer.print("xyz")
            assert sw.getvalue() == "'a,b,c',xyz"

    def test_delimeter_quote_none(self):
        sw = StringWriter()
        format = (
            CSVFormat.DEFAULT
            .with_escape('!')
            .with_quote_mode(QuoteMode.NONE)
        )
        with CSVPrinter(sw, format) as printer:
            printer.print("a,b,c")
            printer.print("xyz")
            assert sw.getvalue() == "a!,b!,c,xyz"

    def test_delimiter_escaped(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_escape('!').with_quote(None)
        with CSVPrinter(sw, format) as printer:
            printer.print("a,b,c")
            printer.print("xyz")
            assert sw.getvalue() == "a!,b!,c,xyz"

    def test_delimiter_plain(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_quote(None)) as printer:
            printer.print("a,b,c")
            printer.print("xyz")
            assert sw.getvalue() == "a,b,c,xyz"

    def test_disabled_comment(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT) as printer:
            printer.print_comment("This is a comment")
            assert sw.getvalue() == ""

    def test_eol_escaped(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(None).with_escape('!')
        with CSVPrinter(sw, format) as printer:
            printer.print("a\rb\nc")
            printer.print("x\fy\bz")
            assert sw.getvalue() == "a!rb!nc,x\fy\bz"

    def test_eol_plain(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_quote(None)) as printer:
            printer.print("a\rb\nc")
            printer.print("x\fy\bz")
            assert sw.getvalue() == "a\rb\nc,x\fy\bz"

    def test_eol_quoted(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_quote('\'')) as printer:
            printer.print("a\rb\nc")
            printer.print("x\by\fz")
            assert sw.getvalue() == "'a\rb\nc',x\by\fz"

    def test_escape_backslash1(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(self.QUOTE_CH)
        with CSVPrinter(sw, format) as printer:
            printer.print("\\")
        assert sw.getvalue() == "\\"

    def test_escape_backslash2(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(self.QUOTE_CH)
        with CSVPrinter(sw, format) as printer:
            printer.print("\\\r")
        assert sw.getvalue() == "'\\\r'"

    def test_escape_backslash3(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(self.QUOTE_CH)
        with CSVPrinter(sw, format) as printer:
            printer.print("X\\\r")
        assert sw.getvalue() == "'X\\\r'"

    def test_escape_backslash4(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(self.QUOTE_CH)
        with CSVPrinter(sw, format) as printer:
            printer.print("\\\\")
        assert sw.getvalue() == "\\\\"

    def test_escape_backslash5(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(self.QUOTE_CH)
        with CSVPrinter(sw, format) as printer:
            printer.print("\\\\")
        assert sw.getvalue() == "\\\\"

    def test_escape_null1(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_escape(None)) as printer:
            printer.print("\\")
        assert sw.getvalue() == "\\"

    def test_escape_null2(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_escape(None)) as printer:
            printer.print("\\\r")
        assert sw.getvalue() == "\"\\\r\""

    def test_escape_null3(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_escape(None)) as printer:
            printer.print("X\\\r")
        assert sw.getvalue() == "\"X\\\r\""

    def test_escape_null4(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_escape(None)) as printer:
            printer.print("\\\\")
        assert sw.getvalue() == "\\\\"

    def test_escape_null5(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_escape(None)) as printer:
            printer.print("\\\\")
        assert sw.getvalue() == "\\\\"

    def test_excel_print_all_array_of_arrays(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.EXCEL) as printer:
            printer.print_records(["r1c1", "r1c2"], ["r2c1", "r2c2"])
            assert (
                sw.getvalue()
                == "r1c1,r1c2" + self.record_separator
                + "r2c1,r2c2" + self.record_separator
            )

    def test_excel_print_all_array_of_lists(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.EXCEL) as printer:
            printer.print_records(["r1c1", "r1c2"], ["r2c1", "r2c2"])
            assert (
                sw.getvalue()
                == "r1c1,r1c2" + self.record_separator
                + "r2c1,r2c2" + self.record_separator
            )

    def test_excel_print_all_iterable_of_arrays(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.EXCEL) as printer:
            printer.print_records(["r1c1", "r1c2"], ["r2c1", "r2c2"])
            assert (
                sw.getvalue()
                == "r1c1,r1c2" + self.record_separator
                + "r2c1,r2c2" + self.record_separator
            )

    def test_excel_print_all_iterable_of_lists(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.EXCEL) as printer:
            printer.print_records(["r1c1", "r1c2"], ["r2c1", "r2c2"])
            assert (
                sw.getvalue()
                == "r1c1,r1c2" + self.record_separator
                + "r2c1,r2c2" + self.record_separator
            )

    def test_excel_printer1(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.EXCEL) as printer:
            printer.print_record("a", "b")
            assert sw.getvalue() == "a,b" + self.record_separator

    def test_excel_printer2(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.EXCEL) as printer:
            printer.print_record("a,b", "b")
            assert sw.getvalue() == "\"a,b\",b" + self.record_separator

    def test_header(self):
        sw = StringWriter()
        format = (
            CSVFormat.DEFAULT
            .with_quote(None)
            .with_header("C1", "C2", "C3")
        )
        with CSVPrinter(sw, format) as printer:
            printer.print_record("a", "b", "c")
            printer.print_record("x", "y", "z")
            assert sw.getvalue() == "C1,C2,C3\r\na,b,c\r\nx,y,z\r\n"

    def test_header_comment_excel(self):
        sw = StringWriter()
        now = datetime.now()
        format = CSVFormat.EXCEL
        with self.print_with_header_comments(sw, now, format) as csv_printer:
            assert sw.getvalue() == (
                "# Generated by Apache Commons CSV 1.1\r\n# " + str(now) +
                "\r\nCol1,Col2\r\nA,B\r\nC,D\r\n"
            )

    def test_header_comment_tdf(self):
        sw = StringWriter()
        now = datetime.now()
        format = CSVFormat.TDF
        with self.print_with_header_comments(sw, now, format) as csv_printer:
            assert sw.getvalue() == (
                "# Generated by Apache Commons CSV 1.1\r\n# " + str(now) +
                "\r\nCol1\tCol2\r\nA\tB\r\nC\tD\r\n"
            )

    def test_header_not_set(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT.with_quote(None)) as printer:
            printer.print_record("a", "b", "c")
            printer.print_record("x", "y", "z")
            assert sw.getvalue() == "a,b,c\r\nx,y,z\r\n"

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            invalid_format = CSVFormat.DEFAULT.with_delimiter('\r')
            with CSVPrinter(StringWriter(), invalid_format) as printer:
                pytest.fail("This test should have thrown an exception.")

    def test_jdbc_printer(self):
        sw = StringWriter()
        connection = self.ge_h2_connection()
        self.set_up_table(connection)
        cursor = connection.cursor()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        result_set = cursor.execute("select ID, NAME from TEST")
        printer.print_records(result_set)
        assert "1,r1" + self.record_separator + "2,r2" + \
            self.record_separator == sw.getvalue()

    def test_jdbc_printer_with_result_set(self):
        sw = StringWriter()
        connection = self.ge_h2_connection()
        self.set_up_table(connection)
        cursor = connection.cursor()
        result_set = cursor.execute("select ID, NAME from TEST")
        printer = CSVFormat.DEFAULT.with_header(result_set).print(sw)
        printer.print_records(result_set)
        assert "ID,NAME" + self.record_separator + \
            "1,r1" + self.record_separator + "2,r2" + \
            self.record_separator == sw.getvalue()

    def test_jdbc_printer_with_result_set_meta_data(self):
        sw = StringWriter()
        connection = self.ge_h2_connection()
        self.set_up_table(connection)
        cursor = connection.cursor()
        result_set = cursor.execute("select ID, NAME from TEST")
        printer = CSVFormat.DEFAULT.with_header(result_set).print(sw)
        printer.print_records(result_set)
        assert "ID,NAME" + self.record_separator + \
            "1,r1" + self.record_separator + "2,r2" + \
            self.record_separator == sw.getvalue()

    @pytest.mark.skip
    def test_jira135_part1(self):
        pass

    @pytest.mark.skip
    def test_jira135_part2(self):
        pass

    @pytest.mark.skip
    def test_jira135_part3(self):
        pass

    @pytest.mark.skip
    def test_jira135_all(self):
        pass

    def test_multi_line_comment(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_comment_marker('#')
        printer = CSVPrinter(sw, format)
        printer.print_comment("This is a comment\non multiple lines")
        expected = "# This is a comment" + self.record_separator + \
                   "# on multiple lines" + self.record_separator
        assert sw.getvalue() == expected

    def test_mysql_null_output(self):
        data = ["NULL", None]
        format = (
            CSVFormat.MYSQL
            .with_quote(self.DQUOTE_CHAR)
            .with_null_string("NULL")
            .with_quote_mode(QuoteMode.NON_NUMERIC)
        )
        writer = StringWriter()
        printer = CSVPrinter(writer, format)
        printer.print_record(*data)
        expected = "\"NULL\"\tNULL\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == [None, None]

        data = ["\\N", None]
        format = CSVFormat.MYSQL.with_null_string("\\N")
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\\\\N\t\\N\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["\\N", "A"]
        format = CSVFormat.MYSQL.with_null_string("\\N")
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\\\\N\tA\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["\n", "A"]
        format = CSVFormat.MYSQL.with_null_string("\\N")
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\\n\tA\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["", None]
        format = CSVFormat.MYSQL.with_null_string("NULL")
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\tNULL\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["", None]
        format = CSVFormat.MYSQL
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\t\\N\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["\\N", "", "\u000e,\\\r"]
        format = CSVFormat.MYSQL
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\\\\N\t\t\u000e,\\\\\\r\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["NULL", "\\\r"]
        format = CSVFormat.MYSQL
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "NULL\t\\\\\\r\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

        data = ["\\\r"]
        format = CSVFormat.MYSQL
        writer = StringWriter()
        with CSVPrinter(writer, format) as printer:
            printer.print_record(*data)
        expected = "\\\\\\r\n"
        assert writer.getvalue() == expected
        record0 = self.to_first_record_values(expected, format)
        assert record0 == self.expect_nulls(data, format)

    @pytest.mark.skip
    def test_postgresql_csv_null_output(self):
        pass

    @pytest.mark.skip
    def test_postgresql_csv_text_output(self):
        pass

    def test_mysql_null_string_default(self):
        assert CSVFormat.MYSQL.get_null_string() == "\\N"

    def test_postgresql_null_string_default_csv(self):
        assert CSVFormat.POSTGRESQL_CSV.get_null_string() == ""

    def test_postgresql_null_string_default_text(self):
        assert CSVFormat.POSTGRESQL_TEXT.get_null_string() == "\\N"

    def test_new_csv_printer_appendable_null_format(self):
        with pytest.raises(ValueError):
            with CSVPrinter(StringWriter(), None):
                pytest.fail("This test should have thrown an exception.")

    def test_new_csv_printer_null_appendable_format(self):
        with pytest.raises(ValueError):
            with CSVPrinter(None, CSVFormat.DEFAULT):
                pytest.fail("This test should have thrown an exception.")

    def test_parse_custom_null_values(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_null_string("NULL")
        with CSVPrinter(sw, format) as printer:
            printer.print_record("a", None, "b")
        csv_string = sw.getvalue()
        assert csv_string == "a,NULL,b" + self.record_separator
        with format.parse(io.StringIO(csv_string)) as iterable:
            iterator = iterable.iterator()
            record = next(iterator)
            assert record.get(0) == "a"
            assert record.get(1) is None
            assert record.get(2) == "b"
            assert not iterator.has_next()

    def test_plain_escaped(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(None).with_escape('!')
        with CSVPrinter(sw, format) as printer:
            printer.print("abc")
            printer.print("xyz")
        expected = "abc,xyz"
        assert sw.getvalue() == expected

    def test_plain_plain(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote(None)
        with CSVPrinter(sw, format) as printer:
            printer.print("abc")
            printer.print("xyz")
        expected = "abc,xyz"
        assert sw.getvalue() == expected

    def test_plain_quoted(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote('\'')
        with CSVPrinter(sw, format) as printer:
            printer.print("abc")
        expected = "abc"
        assert sw.getvalue() == expected

    def test_print(self):
        sw = StringWriter()
        with CSVPrinter(sw, CSVFormat.DEFAULT) as printer:
            printer.print_record("a", "b\\c")
        expected = "a,b\\c" + self.record_separator
        assert sw.getvalue() == expected

    def test_print_custom_null_values(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_null_string("NULL")
        with CSVPrinter(sw, format) as printer:
            printer.print_record("a", None, "b")
        expected = "a,NULL,b" + self.record_separator
        assert sw.getvalue() == expected

    def test_printer1(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a", "b")
        assert sw.getvalue() == "a,b" + self.record_separator

    def test_dont_quote_euro_first_char(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.RFC4180)
        printer.print_record(self.EURO_CH, "Deux")
        expected = self.EURO_CH + ",Deux" + self.record_separator
        assert sw.getvalue() == expected

    def test_quote_comma_first_char(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.RFC4180)
        printer.print_record(",")
        assert sw.getvalue() == "\",\"" + self.record_separator

    def test_printer2(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a,b", "b")
        expected = "\"a,b\",b" + self.record_separator
        assert sw.getvalue() == expected

    def test_printer3(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a, b", "b ")
        expected = "\"a, b\",\"b \"" + self.record_separator
        assert sw.getvalue() == expected

    def test_printer4(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a", "b\"c")
        assert sw.getvalue() == "a,\"b\"\"c\"" + self.record_separator

    def test_printer5(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a", "b\nc")
        assert sw.getvalue() == "a,\"b\nc\"" + self.record_separator

    def test_printer6(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a", "b\r\nc")
        assert sw.getvalue() == "a,\"b\r\nc\"" + self.record_separator

    def test_printer7(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a", "b\\c")
        assert sw.getvalue() == "a,b\\c" + self.record_separator

    def test_print_null_values(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT)
        printer.print_record("a", None, "b")
        assert sw.getvalue() == "a,,b" + self.record_separator

    def test_print_one_positive_integer(self):
        sw = StringWriter()
        printer = CSVPrinter(sw, CSVFormat.DEFAULT.with_quote_mode(QuoteMode.MINIMAL))
        printer.print(str(sys.maxsize))
        assert sw.getvalue() == str(sys.maxsize)

    def test_print_to_file_with_charset_utf16_be(self):
        file = open(self.__class__.__name__ + ".csv", "w", encoding='utf-16be')
        with CSVFormat.DEFAULT.print(file, 'utf-16be') as printer:
            printer.print_record("a", "b\\c")
        
        with open(file.name, encoding='utf-16be', newline='') as f:
            assert f.read() == "a,b\\c" + self.record_separator
        
        os.remove(file.name)

    def test_print_to_file_with_default_charset(self):
        file = open(self.__class__.__name__ + ".csv", "w")
        with CSVFormat.DEFAULT.print(file, locale.getpreferredencoding()) as printer:
            printer.print_record("a", "b\\c")
            
        with open(file.name, encoding=locale.getpreferredencoding(), newline='') as f:
            assert f.read() == "a,b\\c" + self.record_separator
            
        os.remove(file.name)

    def test_print_to_path_with_default_charset(self):
        file = open(self.__class__.__name__ + ".csv", "w")
        with CSVFormat.DEFAULT.print(Path(file.name), locale.getpreferredencoding()) as printer:
            printer.print_record("a", "b\\c")
            
        with open(file.name, encoding=locale.getpreferredencoding(), newline='') as f:
            assert f.read() == "a,b\\c" + self.record_separator
        
        os.remove(file.name)

    def test_quote_all(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote_mode(QuoteMode.ALL)
        with CSVPrinter(sw, format) as printer:
            printer.print_record("a", "b\nc", "d")
        expected_value = "\"a\",\"b\nc\",\"d\"" + self.record_separator
        assert sw.getvalue() == expected_value

    def test_quote_non_numeric(self):
        sw = StringWriter()
        format = CSVFormat.DEFAULT.with_quote_mode(QuoteMode.NON_NUMERIC)
        with CSVPrinter(sw, format) as printer:
            printer.print_record("a", "b\nc", 1)
        assert sw.getvalue() == "\"a\",\"b\nc\",1" + self.record_separator

    def test_random_default(self):
        self.do_random(CSVFormat.DEFAULT, self.ITERATIONS_FOR_RANDOM_TEST)

    def test_random_excel(self):
        self.do_random(CSVFormat.EXCEL, self.ITERATIONS_FOR_RANDOM_TEST)

    def test_random_mysql(self):
        self.do_random(CSVFormat.MYSQL, self.ITERATIONS_FOR_RANDOM_TEST)

    @pytest.mark.skip
    def test_random_oracle(self):
        pass
    
    @pytest.mark.skip
    def test_random_postgresql_csv(self):
        pass

    @pytest.mark.skip
    def test_random_postgresql_text(self):
        pass

    def test_random_rfc4180(self):
        self.do_random(
            CSVFormat.RFC4180,
            self.ITERATIONS_FOR_RANDOM_TEST
        )

    def test_random_tdf(self):
        self.do_random(
            CSVFormat.TDF,
            self.ITERATIONS_FOR_RANDOM_TEST
        )

    def test_single_line_comment(self):
        output = StringWriter()
        comment_marker = CSVFormat.DEFAULT.with_comment_marker('#')
        with CSVPrinter(output, comment_marker) as printer:
            printer.print_comment("This is a comment")
            expected = "# This is a comment" + self.record_separator
            assert output.getvalue() == expected

    def test_single_quote_quoted(self):
        output = StringWriter()
        quote = CSVFormat.DEFAULT.with_quote('\'')
        with CSVPrinter(output, quote) as printer:
            printer.print("a'b'c")
            printer.print("xyz")
            assert output.getvalue() == "'a''b''c',xyz"

    def test_skip_header_record_false(self):
        output = StringWriter()
        header = ["C1", "C2", "C3"]
        format = (
            CSVFormat.DEFAULT
            .with_quote(None)
            .with_header(*header)
            .with_skip_header_record(False)
        )
        with CSVPrinter(output, format) as printer:
            printer.print_record("a", "b", "c")
            printer.print_record("x", "y", "z")
            assert (
                output.getvalue() ==
                f"{','.join(header)}\r\n"
                f"a,b,c\r\n"
                f"x,y,z\r\n"
            )

    def test_skip_header_record_true(self):
        output = StringWriter()
        format = (
            CSVFormat.DEFAULT
            .with_quote(None)
            .with_header("C1", "C2", "C3")
            .with_skip_header_record(True)
        )
        with CSVPrinter(output, format) as printer:
            printer.print_record("a", "b", "c")
            printer.print_record("x", "y", "z")
            assert output.getvalue() == (
                f"a,b,c\r\n"
                f"x,y,z\r\n"
            )

    def test_trailing_delimiter_on_two_columns(self):
        output = StringWriter()
        formatter = CSVFormat.DEFAULT.with_trailing_delimiter()
        with CSVPrinter(output, formatter) as printer:
            printer.print_record("A", "B")
            assert output.getvalue() == "A,B,\r\n"

    def test_trim_off_one_column(self):
        output = StringWriter()
        with CSVPrinter(output, CSVFormat.DEFAULT.with_trim(False)) as printer:
            printer.print(" A ")
            assert output.getvalue() == "\" A \""

    def test_trim_on_one_column(self):
        output = StringWriter()
        with CSVPrinter(output, CSVFormat.DEFAULT.with_trim()) as printer:
            printer.print(" A ")
            assert output.getvalue() == "A"

    def test_trim_on_two_columns(self):
        output = StringWriter()
        with CSVPrinter(output, CSVFormat.DEFAULT.with_trim()) as printer:
            printer.print(" A ")
            printer.print(" B ")
            assert output.getvalue() == "A,B"

    def test_print_records_with_result_set_one_row(self):
        csv_printer = CSVFormat.MYSQL.printer()
        cur = sqlite3.connect(':memory:').cursor()
        csv_printer.print_records(cur)
        assert len(cur.fetchall()) == 0

    def test_print_records_with_object_array(self):
        char_array_writer = StringWriter()
        with CSVFormat.INFORMIX_UNLOAD.print(char_array_writer) as csv_printer:
            hash_set = set()
            object_array = [None] * 6
            object_array[3] = hash_set
            csv_printer.print_records(*object_array)
        v = char_array_writer.getvalue()
        assert len(v) == 6
        assert v == "\n" * 6        

    def test_print_records_with_empty_vector(self):
        output = StringWriter()
        with CSVPrinter(output, CSVFormat.POSTGRESQL_TEXT) as csv_printer:
            expected_capacity = 23
            vector = [None] * expected_capacity
            csv_printer.print_records(vector)
            assert len(vector) == expected_capacity

    def test_close_with_flush_on(self):
        writer = Mock()
        csv_format = CSVFormat.DEFAULT
        csv_printer = CSVPrinter(writer, csv_format)
        csv_printer.close(flush=True)
        writer.flush.assert_called_once()

    def test_close_with_flush_off(self):
        writer = Mock()
        csv_format = CSVFormat.DEFAULT
        csv_printer = CSVPrinter(writer, csv_format)
        csv_printer.close(flush=False)
        writer.flush.assert_not_called()
        writer.close.assert_called_once()

    def test_close_backward_compatibility(self):
        writer = Mock()
        csv_format = CSVFormat.DEFAULT
        with CSVPrinter(writer, csv_format) as csv_printer:
            pass
        writer.flush.assert_not_called()
        writer.close.assert_called_once()

    def test_close_with_csv_format_auto_flush_on(self):
        writer = Mock()
        csv_format = CSVFormat.DEFAULT.with_auto_flush(True)
        with CSVPrinter(writer, csv_format) as csv_printer:
            pass
        writer.flush.assert_called_once()
        writer.close.assert_called_once()

    def test_close_with_csv_format_auto_flush_off(self):
        writer = Mock()
        csv_format = CSVFormat.DEFAULT.with_auto_flush(False)
        with CSVPrinter(writer, csv_format) as csv_printer:
            pass
        writer.flush.assert_not_called()
        writer.close.assert_called_once()