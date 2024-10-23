import io
import locale
import os
import pytest
from pathlib import Path
from main.python.constants import Constants
from main.python.csv_parser import CSVParser
from main.python.csv_format import CSVFormat
from main.python.csv_printer import CSVPrinter
from test.python.utils import Utils


BASE = Path(__file__).parent.parent / "resources"

class TestCSVParser:
    """
    The test are organized in three different sections: The 'setter/getter' section, 
    the lexer section and finally the parser section. In case a test fails, you 
    should follow a top-down approach for fixing a potential bug (its likely
    that the parser itself fails if the lexer has problems...).
    """
    
    UTF_8 = "utf-8"
    UTF_8_NAME = "utf-8-sig"
    
    CSV_INPUT = ("a,b,c,d\n"
             " a , b , 1 2 \n"
             "\"foo baar\", b,\n"
             "   \"foo\n,,\n\"\",,\n"
             "\"\"\",d,e\n")
    CSV_INPUT_1 = "a,b,c,d"
    CSV_INPUT_2 = "a,b,1 2"
    RESULT = [
        ['a', 'b', 'c', 'd'],
        ['a', 'b', '1 2'],
        ['foo baar', 'b', ''],
        ['foo\n,,\n",,\n"', 'd', 'e']
    ]
    
    def create_bom_input_stream(self, resource):
        return open(
             str(BASE) + "/"
             + resource, 
            'r', 
            encoding=TestCSVParser.UTF_8_NAME
        )

    def test_backslash_escaping(self):
        """
        To avoid confusion over the need for escaping chars in java code,
        We will test with a forward slash as the escape char, and a single
        quote as the encapsulator.
        """

        code = (
            "one,two,three\n"  # 0
            + "'',''\n"  # 1) empty encapsulators
            + "/',/'\n"  # 2) single encapsulators
            + "'/'','/''\n"  # 3) single encapsulators encapsulated via escape
            + "'''',''''\n"  # 4) single encapsulators encapsulated via doubling
            + "/,,/,\n"  # 5) separator escaped
            + "//,//\n"  # 6) escape escaped
            + "'//','//'\n"  # 7) escape escaped in encapsulation
            + "   8   ,   \"quoted \"\" /\" // string\"   \n"  # don't eat spaces
            + "9,   /\n   \n"  # escaped newline
            + ""
        )
        res = [
            ["one", "two", "three"],  # 0
            ["", ""],  # 1
            ["'", "'"],  # 2
            ["'", "'"],  # 3
            ["'", "'"],  # 4
            [",", ","],  # 5
            ["/", "/"],  # 6
            ["/", "/"],  # 7
            ["   8   ", '   "quoted "" /" / string"   '],
            ["9", "   \n   "],
        ]

        csv_format = (CSVFormat.new_format(",").with_quote("'")
                      .with_record_separator(Constants.CRLF).with_escape("/")
                      .with_ignore_empty_lines())

        with CSVParser.parse(code, csv_format) as parser:
            records = parser.get_records()
            assert len(records) > 0

            Utils.compare("Records do not match expected result", res, records)

    def test_backslash_escaping_2(self):
        # To avoid confusion over the need for escaping chars in Python code,
        # We will test with a forward slash as the escape char, and a single
        # quote as the encapsulator.

        code = (
            " , , \n"      # 1
            " \t ,  , \n"  # 2
            " // , /, , /,\n"  # 3
        )
        res = [
            [" ", " ", " "],        # 1
            [" \t ", "  ", " "],    # 2
            [" / ", " , ", " ,"],   # 3
        ]

        format = (CSVFormat.new_format(',').with_record_separator(Constants.CRLF)
                  .with_escape('/').with_ignore_empty_lines())

        with CSVParser.parse(code, format) as parser:
            records = parser.get_records()
            assert len(records) > 0

            Utils.compare("", res, records)

    @pytest.mark.skip
    def test_backslash_escaping_old(self):
        pass

    @pytest.mark.skip
    def test_bom(self):
        pass
    
    def test_bom_input_stream_parser_with_reader(self):
        with self.create_bom_input_stream("CSVFileParser/bom.csv") as reader:
            parser = CSVParser(reader, CSVFormat.EXCEL.with_header())
            for record in parser:
                string = record.get("Date")
                assert string is not None
                
    def test_bom_input_stream_parse_with_reader(self):
        with self.create_bom_input_stream("CSVFileParser/bom.csv") as reader:
            parser = CSVParser.parse(reader, CSVFormat.EXCEL.with_header())
            for record in parser:
                string = record.get("Date")
                assert string is not None

    def test_bom_input_stream_parser_with_input_stream(self):
        with self.create_bom_input_stream("CSVFileParser/bom.csv") as input_stream:
            parser = CSVParser.parse(input_stream, TestCSVParser.UTF_8, CSVFormat.EXCEL.with_header())
            for record in parser:
                string = record.get("Date")
                assert string is not None

    def test_carriage_return_endings(self):
        data = "foo\rbaar,\rhello,world\r,kanu"
        with CSVParser.parse(data, CSVFormat.DEFAULT) as parser:
            records = parser.get_records()
            assert len(records) == 4

    def test_carriage_return_line_feed_endings(self):
        data = "foo\r\nbaar,\r\nhello,world\r\n,kanu"
        with CSVParser.parse(data, CSVFormat.DEFAULT) as parser:
            records = parser.get_records()
            assert len(records) == 4

    def test_first_end_of_line_crlf(self):
        data = "foo\r\nbaar,\r\nhello,world\r\n,kanu"
        with CSVParser.parse(data, CSVFormat.DEFAULT) as parser:
            records = list(parser)
            assert len(records) == 4
            assert parser.get_first_end_of_line() == "\r\n"

    def test_first_end_of_line_lf(self):
        data = "foo\nbaar,\nhello,world\n,kanu"
        with CSVParser.parse(data, CSVFormat.DEFAULT) as parser:
            records = list(parser)
            assert len(records) == 4
            assert parser.get_first_end_of_line() == "\n"

    def test_first_end_of_line_cr(self):
        data = "foo\rbaar,\rhello,world\r,kanu"
        with CSVParser.parse(data, CSVFormat.DEFAULT) as parser:
            records = parser.get_records()
            assert len(records) == 4
            assert parser.get_first_end_of_line() == "\r"

    def test_close(self):
        inp = io.StringIO("# comment\na,b,c\n1,2,3\nx,y,z")
        with CSVFormat.DEFAULT.with_comment_marker('#').with_header().parse(inp) as parser:
            records = iter(parser)
            assert next(records)
        
        with pytest.raises(StopIteration):
            next(records)

    def test_csv57(self):
        with CSVParser.parse("", CSVFormat.DEFAULT) as parser:
            records = parser.get_records()
            assert records is not None
            assert len(records) == 0

    def test_default_format(self):
        code = (
            "a,b#\n"  # 1
            "\"\n\",\" \",#\n"  # 2
            "#,\"\"\n"  # 3
            "# Final comment\n"  # 4
        )
        res = [["a", "b#"], ["\n", " ", "#"], ["#", ""], ["# Final comment"]]
        
        format = CSVFormat.DEFAULT
        assert not format.is_comment_marker_set()
        res_comments = [["a", "b#"], ["\n", " ", "#"]]

        with CSVParser.parse(code, format) as parser:
            records = parser.get_records()
            assert len(records) > 0

            Utils.compare("Failed to parse without comments", res, records)
            
            format = CSVFormat.DEFAULT.with_comment_marker('#')

        with CSVParser.parse(code, format) as parser:
            records = parser.get_records()

            Utils.compare("Failed to parse with comments", res_comments, records)

    def test_duplicate_headers(self):
        with pytest.raises(ValueError):
            CSVParser.parse("a,b,a\n1,2,3\nx,y,z", CSVFormat.DEFAULT.with_header(*[]))

    def test_empty_file(self):
        with CSVParser.parse("", CSVFormat.DEFAULT) as parser:
            assert parser.next_record() is None

    def test_empty_line_behaviour_csv(self):
        codes = [
            "hello,\r\n\r\n\r\n",
            "hello,\n\n\n",
            "hello,\"\"\r\n\r\n\r\n",
            "hello,\"\"\n\n\n"
        ]
        res = [["hello", ""]]  # CSV format ignores empty lines

        for code in codes:
            with CSVParser.parse(code, CSVFormat.DEFAULT) as parser:
                records = list(parser)
                assert len(res) == len(records)
                assert len(records) > 0
                for i in range(len(res)):
                    assert res[i] == records[i].values()

    def test_empty_line_behaviour_excel(self):
        codes = [
            "hello,\r\n\r\n\r\n",
            "hello,\n\n\n",
            "hello,\"\"\r\n\r\n\r\n",
            "hello,\"\"\n\n\n"
        ]
        res = [['hello', ''], [''], ['']]
        for code in codes:
            with CSVParser.parse(code, CSVFormat.EXCEL) as parser:
                records = list(parser)
                assert len(res) == len(records)
                assert len(records) > 0
                for i in range(len(res)):
                    assert res[i] == records[i].values()

    def test_end_of_file_behaviour_csv(self):
        codes = [
            "hello,\r\n\r\nworld,\r\n",
            "hello,\r\n\r\nworld,",
            "hello,\r\n\r\nworld,\"\"\r\n",
            "hello,\r\n\r\nworld,\"\"",
            "hello,\r\n\r\nworld,\n",
            "hello,\r\n\r\nworld,",
            "hello,\r\n\r\nworld,\"\"\n",
            "hello,\r\n\r\nworld,\"\""
        ]
        res = [
            ["hello", ""],  # CSV format ignores empty lines
            ["world", ""]
        ]
        for code in codes:
            with CSVParser.parse(code, CSVFormat.DEFAULT) as parser:
                records = list(parser)
                assert len(res) == len(records)
                assert len(records) > 0
                for i in range(len(res)):
                    assert res[i] == records[i].values()

    def test_end_of_file_behavior_excel(self):
        codes = [
            "hello,\r\n\r\nworld,\r\n",
            "hello,\r\n\r\nworld,",
            "hello,\r\n\r\nworld,\"\"\r\n",
            "hello,\r\n\r\nworld,\"\"",
            "hello,\r\n\r\nworld,\n",
            "hello,\r\n\r\nworld,",
            "hello,\r\n\r\nworld,\"\"\n",
            "hello,\r\n\r\nworld,\"\""
        ]
        res = [
            ["hello", ""],
            [""],  # Excel format does not ignore empty lines
            ["world", ""]
        ]

        for code in codes:
            with CSVParser.parse(code, CSVFormat.EXCEL) as parser:
                records = list(parser)
                assert len(res) == len(records)
                assert len(records) > 0
                for i in range(len(res)):
                    assert res[i] == records[i].values()

    def test_excel_format_1(self):
        code = "value1,value2,value3,value4\r\na,b,c,d\r\n  x,,," \
            "\r\n\r\n\"\"\"hello\"\"\",\"  \"\"world\"\"\",\"abc\ndef\",\r\n"
        res = [
            ["value1", "value2", "value3", "value4"],
            ["a", "b", "c", "d"],
            ["  x", "", "", ""],
            [""],
            ["\"hello\"", "  \"world\"", "abc\ndef", ""]
        ]

        with CSVParser.parse(code, CSVFormat.EXCEL) as parser:
            records = parser.get_records()
            assert len(res) == len(records)
            assert len(records) > 0
            for i in range(len(res)):
                assert res[i] == records[i].values()

    def test_excel_format_2(self):
        code = "foo,baar\r\n\r\nhello,\r\n\r\nworld,\r\n"
        res = [
            ["foo", "baar"],
            [""],
            ["hello", ""],
            [""],
            ["world", ""]
        ]

        with CSVParser.parse(code, CSVFormat.EXCEL) as parser:
            records = parser.get_records()
            assert len(res) == len(records)
            assert len(records) > 0
            for i in range(len(res)):
                assert res[i] == records[i].values()

    def test_excel_header_count_less_than_data(self):
        """
        Tests an exported Excel worksheet with a header row 
        and rows that have more columns than the headers
        """
        code = "A,B,C,,\r\na,b,c,d,e\r\n"

        with CSVParser.parse(code, CSVFormat.EXCEL.with_header()) as parser:
            for record in parser.get_records():
                assert record.get("A") == "a"
                assert record.get("B") == "b"
                assert record.get("C") == "c"

    def test_for_each(self):
        records = []
        with io.StringIO("a,b,c\n1,2,3\nx,y,z") as inp:
            for record in CSVFormat.DEFAULT.parse(inp):
                records.append(record)

        assert len(records) == 3
        assert records[0].values() == ["a", "b", "c"]
        assert records[1].values() == ["1", "2", "3"]
        assert records[2].values() == ["x", "y", "z"]

    def test_get_header_map(self):
        parser = CSVParser.parse("a,b,c\n1,2,3\nx,y,z", CSVFormat.DEFAULT.with_header("A", "B", "C"))
        header_map = parser.get_header_map()
        column_names = iter(header_map.keys())
        # Headers are iterated in column order.
        assert next(column_names) == "A"
        assert next(column_names) == "B"
        assert next(column_names) == "C"

        records = parser.iterator()

        # Parse to make sure get_header_map did not have a side-effect.
        for i in range(3):
            assert records.has_next()
            record = next(records)
            assert record.get(0) == record.get("A")
            assert record.get(1) == record.get("B")
            assert record.get(2) == record.get("C")

        assert not records.has_next()

    def test_get_line(self):
        with CSVParser.parse(TestCSVParser.CSV_INPUT, CSVFormat.DEFAULT.with_ignore_surrounding_spaces()) as parser:
            for re in TestCSVParser.RESULT:
                assert parser.next_record().values() == re

            assert parser.next_record() is None

    def test_get_line_number_with_cr(self):
        self.validate_line_numbers(Constants.CR)

    def test_get_line_number_with_crlf(self):
        self.validate_line_numbers(Constants.CRLF)

    def test_get_line_number_with_lf(self):
        self.validate_line_numbers(Constants.LF)

    def test_get_one_line(self):
        with CSVParser.parse(TestCSVParser.CSV_INPUT_1, CSVFormat.DEFAULT) as parser:
            record = parser.get_records()[0]
            assert record.values() == TestCSVParser.RESULT[0]

    def test_get_one_line_one_parser(self):
        """
        Tests reusing a parser to process new string records one at a 
        time as they are being discovered.
        """
        format = CSVFormat.DEFAULT
        with io.StringIO() as writer, CSVParser(writer, format) as parser:
            writer.write(TestCSVParser.CSV_INPUT_1)
            writer.write(format.get_record_separator())
            record1 = parser.next_record()
            assert record1.values() == TestCSVParser.RESULT[0]
            writer.write(TestCSVParser.CSV_INPUT_2)
            writer.write(format.get_record_separator())
            record2 = parser.next_record()
            assert record2.values() == TestCSVParser.RESULT[1]

    def test_get_record_number_with_CR(self):
        self.validate_record_numbers(Constants.CR)

    def test_get_record_number_with_CRLF(self):
        self.validate_record_numbers(Constants.CRLF)

    def test_get_record_number_with_LF(self):
        self.validate_record_numbers(Constants.LF)

    def test_get_record_position_with_CRLF(self):
        self.validate_record_position(Constants.CRLF)

    def test_get_record_position_with_LF(self):
        self.validate_record_position(Constants.LF)

    def test_get_records(self):
        with CSVParser.parse(TestCSVParser.CSV_INPUT, CSVFormat.DEFAULT.with_ignore_surrounding_spaces()) as parser:
            records = parser.get_records()
            assert len(TestCSVParser.RESULT) == len(records)
            assert len(records) > 0
            for i in range(len(TestCSVParser.RESULT)):
                assert TestCSVParser.RESULT[i] == list(records[i].values())

    def test_get_record_with_multi_line_values(self):
        csv_input = "\"a\r\n1\",\"a\r\n2\"" + Constants.CRLF + "\"b\r\n1\",\"b\r\n2\"" + Constants.CRLF + "\"c\r\n1\",\"c\r\n2\""
        format = CSVFormat.DEFAULT.with_record_separator(Constants.CRLF)
        with CSVParser.parse(csv_input, format) as parser:
            assert 0 == parser.get_record_number()
            assert 0 == parser.get_current_line_number()
            record = parser.next_record()
            assert record is not None
            assert 3 == parser.get_current_line_number()
            assert 1 == record.get_record_number()
            assert 1 == parser.get_record_number()
            record = parser.next_record()
            assert record is not None
            assert 6 == parser.get_current_line_number()
            assert 2 == record.get_record_number()
            assert 2 == parser.get_record_number()
            record = parser.next_record()
            assert record is not None
            assert 8 == parser.get_current_line_number()
            assert 3 == record.get_record_number()
            assert 3 == parser.get_record_number()
            record = parser.next_record()
            assert record is None
            assert 8 == parser.get_current_line_number()
            assert 3 == parser.get_record_number()
            assert record is None

    def test_header(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header().parse(inp).iterator()
        
        for i in range(2):
            record = next(records)
            assert record.get("a") == record.get(0)
            assert record.get("b") == record.get(1)
            assert record.get("c") == record.get(2)
        
        try:
            next(records)
            assert False
        except StopIteration:
            pass

    def test_header_comment(self):
        inp = io.StringIO("# comment\na,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_comment_marker('#').with_header().parse(inp).iterator()
        
        for i in range(2):
            record = next(records)
            assert record.get("a") == record.get(0)
            assert record.get("b") == record.get(1)
            assert record.get("c") == record.get(2)
            
        try:
            next(records)
            assert False
        except StopIteration:
            pass

    def test_header_missing(self):
        inp = io.StringIO("a,,c\n1,2,3\nx,y,z")
        
        records = CSVFormat.DEFAULT.with_header().parse(inp).iterator()

        for i in range(2):
            record = next(records)
            assert record.get("a") == record.get(0)
            assert record.get("c") == record.get(2)
            
        try:
            next(records)
            assert False
        except StopIteration:
            pass
        
    def test_header_missing_with_null(self):
        inp = io.StringIO("a,,c,,d\n1,2,3,4\nx,y,z,zz")
        CSVFormat.DEFAULT.with_header().with_null_string("").with_allow_missing_column_names().parse(inp).iterator()

    def test_headers_missing(self):
        inp = io.StringIO("a,,c,,d\n1,2,3,4\nx,y,z,zz")
        CSVFormat.DEFAULT.with_header().with_allow_missing_column_names().parse(inp).iterator()

    def test_headers_missing_exception(self):
        inp = io.StringIO("a,,c,,d\n1,2,3,4\nx,y,z,zz")
        with pytest.raises(ValueError):
            CSVFormat.DEFAULT.with_header().parse(inp).iterator()

    def test_ignore_case_header_mapping(self):
        inp = io.StringIO("1,2,3")
        records = CSVFormat.DEFAULT.with_header("One", "TWO", "three").with_ignore_header_case().parse(inp).iterator()
        record = next(records)
        assert record.get("one") == "1"
        assert record.get("two") == "2"
        assert record.get("THREE") == "3"

    def test_ignore_empty_lines(self):
        csv_input = "\nfoo,baar\n\r\n,\n\n,world\r\n\n"
        # code = "world\r\n\n"
        # code = "foo;baar\r\n\r\nhello;\r\n\r\nworld;\r\n"
        with CSVParser.parse(csv_input, CSVFormat.DEFAULT) as parser:
            records = parser.get_records()
            assert len(records) == 3

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            invalid_format = CSVFormat.DEFAULT.with_delimiter(Constants.CR)
            with CSVParser.parse(TestCSVParser.CSV_INPUT, invalid_format):
                pytest.fail("This test should have raised an exception.")

    def test_iterator(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        iterator = CSVFormat.DEFAULT.parse(inp).iterator()
        
        assert iterator.has_next()
        try:
            iterator.remove()
            pytest.fail("expected NotImplementedError")
        except NotImplementedError:
            pass # expected
        
        assert next(iterator).values() == ["a", "b", "c"]
        assert next(iterator).values() == ["1", "2", "3"]
        assert iterator.has_next()
        assert iterator.has_next()
        assert iterator.has_next()
        assert next(iterator).values() == ["x", "y", "z"]
        assert not iterator.has_next()
        
        try:
            next(iterator)
            pytest.fail("StopIteration expected")
        except StopIteration:
            pass # expected

    def test_line_feed_endings(self):
        code = "foo\nbaar,\nhello,world\n,kanu"
        with CSVParser.parse(code, CSVFormat.DEFAULT) as parser:
            records = parser.get_records()
            assert len(records) == 4

    def test_mapped_but_not_set_as_outlook_2007_contact_export(self):
        inp = io.StringIO("a,b,c\n1,2\nx,y,z")
        records = CSVFormat.DEFAULT.with_header("A", "B", "C").with_skip_header_record().parse(inp).iterator()

        # 1st record
        record = next(records)
        assert record.is_mapped("A")
        assert record.is_mapped("B")
        assert record.is_mapped("C")
        assert record.is_set("A")
        assert record.is_set("B")
        assert not record.is_set("C")
        assert record.get("A") == "1"
        assert record.get("B") == "2"
        assert not record.is_consistent()

        # 2nd record
        record = next(records)
        assert record.is_mapped("A")
        assert record.is_mapped("B")
        assert record.is_mapped("C")
        assert record.is_set("A")
        assert record.is_set("B")
        assert record.is_set("C")
        assert record.get("A") == "x"
        assert record.get("B") == "y"
        assert record.get("C") == "z"
        assert record.is_consistent()
        
        assert not records.has_next()
        

    def test_multiple_iterators(self):
        csv_input = "a,b,c" + Constants.CR + "d,e,f"
        with CSVParser.parse(csv_input, CSVFormat.DEFAULT) as parser:
            itr1 = iter(parser)
            itr2 = iter(parser)

            first = next(itr1)
            assert first.get(0) == "a"
            assert first.get(1) == "b"
            assert first.get(2) == "c"

            second = next(itr2)
            assert second.get(0) == "d"
            assert second.get(1) == "e"
            assert second.get(2) == "f"

    def test_new_csv_parser_null_reader_format(self):
        with pytest.raises(ValueError):
            with CSVParser(None, CSVFormat.DEFAULT):
                assert False, "This test should have raised an exception."

    def test_new_csv_parser_reader_null_format(self):
        with pytest.raises(ValueError):
            with CSVParser(io.StringIO(""), None):
                assert False, "This test should have raised an exception."

    def test_no_header_map(self):
        csv_input = "a,b,c\n1,2,3\nx,y,z"
        with CSVParser.parse(csv_input, CSVFormat.DEFAULT) as parser:
            assert parser.get_header_map() is None

    def test_parse_file_null_format(self):
        with pytest.raises(ValueError):
            CSVParser.parse("", locale.getpreferredencoding(), None)

    def test_parse_null_file_format(self):
      with pytest.raises(ValueError):
          CSVParser.parse(None, None, CSVFormat.DEFAULT)
  
    def test_parse_null_string_format(self):
        with pytest.raises(ValueError):
            CSVParser.parse(None, CSVFormat.DEFAULT)
    
    def test_parse_null_url_charset_format(self):
        with pytest.raises(ValueError):
            CSVParser.parse(None, None, CSVFormat.DEFAULT)
    
    def test_parser_url_null_charset_format(self):
        with pytest.raises(ValueError):
            with CSVParser.parse("http://commons.apache.org", None, CSVFormat.DEFAULT) as parser:
                assert False, "This test should have raised an exception."
    
    def test_parse_string_null_format(self):
        with pytest.raises(ValueError):
            CSVParser.parse("csv data", None)
    
    def test_parse_url_charset_null_format(self):
        with pytest.raises(ValueError):
            with CSVParser.parse("http://commons.apache.org", locale.getpreferredencoding(), None) as parser:
                assert False, "This test should have raised an exception."
    
    def test_provided_header(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header("A", "B", "C").parse(inp).iterator()
        
        for i in range(3):
            assert records.has_next()
            record = next(records)
            assert record.is_mapped("A")
            assert record.is_mapped("B")
            assert record.is_mapped("C")
            assert not record.is_mapped("NOT MAPPED")
            assert record.get("A") == record.get(0)
            assert record.get("B") == record.get(1)
            assert record.get("C") == record.get(2)
        assert not records.has_next()

    def test_provided_header_auto(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header().parse(inp).iterator()

        for i in range(2):
            assert records.has_next()
            record = next(records)
            assert record.is_mapped("a")
            assert record.is_mapped("b")
            assert record.is_mapped("c")
            assert not record.is_mapped("NOT MAPPED")
            assert record.get("a") == record.get(0)
            assert record.get("b") == record.get(1)
            assert record.get("c") == record.get(2)
        assert not records.has_next()

    def test_roundtrip(self):
        out = io.StringIO()
        with CSVPrinter(out, CSVFormat.DEFAULT) as printer:
            inp = "a,b,c\r\n1,2,3\r\nx,y,z\r\n"
            for record in CSVParser.parse(inp, CSVFormat.DEFAULT):
                printer.print_record(record)
            assert out.getvalue() == inp

    def test_skip_auto_header(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header().parse(inp).iterator()
        record = next(records)
        assert "1" == record.get("a")
        assert "2" == record.get("b")
        assert "3" == record.get("c")

    def test_skip_header_override_duplicate_headers(self):
        inp = io.StringIO("a,a,a\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header("X", "Y", "Z").with_skip_header_record().parse(inp).iterator()
        record = next(records)
        assert "1" == record.get("X")
        assert "2" == record.get("Y")
        assert "3" == record.get("Z")

    def test_skip_set_alt_headers(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header("X", "Y", "Z").with_skip_header_record().parse(inp).iterator()
        record = next(records)
        assert "1" == record.get("X")
        assert "2" == record.get("Y")
        assert "3" == record.get("Z")

    def test_skip_set_header(self):
        inp = io.StringIO("a,b,c\n1,2,3\nx,y,z")
        records = CSVFormat.DEFAULT.with_header("a", "b", "c").with_skip_header_record().parse(inp).iterator()
        record = next(records)
        assert "1" == record.get("a")
        assert "2" == record.get("b")
        assert "3" == record.get("c")

    @pytest.mark.skip
    def test_start_with_empty_lines_then_headers(self):
        pass

    def test_trailing_delimiter(self):
        inp = io.StringIO("a,a,a,\n\"1\",\"2\",\"3\",\nx,y,z,")
        records = CSVFormat.DEFAULT.with_header("X", "Y", "Z").with_skip_header_record().with_trailing_delimiter().parse(inp).iterator()
        record = next(records)
        assert "1" == record.get("X")
        assert "2" == record.get("Y")
        assert "3" == record.get("Z")
        assert 3 == record.size()

    def test_trim(self):
        inp = io.StringIO("a,a,a\n\" 1 \",\" 2 \",\" 3 \"\nx,y,z")
        records = CSVFormat.DEFAULT.with_header("X", "Y", "Z").with_skip_header_record().with_trim().parse(inp).iterator()
        record = next(records)
        assert "1" == record.get("X")
        assert "2" == record.get("Y")
        assert "3" == record.get("Z")
        assert 3 == record.size()

    def test_iterator_sequence_breaking(self):
        five_rows = "1\n2\n3\n4\n5\n"

        # Iterator hasNext() shouldn't break sequence
        parser = CSVFormat.DEFAULT.parse(io.StringIO(five_rows))
        record_number = 0
        iterator = iter(parser)
        while iterator.has_next():
            record = next(iterator)
            record_number += 1
            assert str(record_number) == record.get(0)
            if record_number >= 2:
                break
            
        iterator.has_next()
        while iterator.has_next():
            record = next(iterator)
            record_number += 1
            assert str(record_number) == record.get(0)

        # Consecutive enhanced for loops shouldn't break sequence
        parser = CSVFormat.DEFAULT.parse(io.StringIO(five_rows))
        record_number = 0
        for record in parser:
            record_number += 1
            assert str(record_number) == record.get(0)
            if record_number >= 2:
                break
        for record in parser:
            record_number += 1
            assert str(record_number) == record.get(0)

        # Consecutive enhanced for loops with hasNext() peeking 
        # shouldn't break sequence
        parser = CSVFormat.DEFAULT.parse(io.StringIO(five_rows))
        record_number = 0
        for record in parser:
            record_number += 1
            assert str(record_number) == record.get(0)
            if record_number >= 2:
                break
        parser.iterator().has_next()
        for record in parser:
            record_number += 1
            assert str(record_number) == record.get(0)

    def validate_line_numbers(self, line_separator):
        csv_data = f"a{line_separator}b{line_separator}c"

        with CSVParser.parse(csv_data, CSVFormat.DEFAULT
                                    .with_record_separator(line_separator)) as parser:
            assert 0 == parser.get_current_line_number()
            assert parser.next_record() is not None
            assert 1 == parser.get_current_line_number()
            assert parser.next_record() is not None
            assert 2 == parser.get_current_line_number()
            assert parser.next_record() is not None
            # Still 2 because the last line does not have EOL chars
            assert 2 == parser.get_current_line_number()
            assert parser.next_record() is None
            # Still 2 because the last line does not have EOL chars
            assert 2 == parser.get_current_line_number()

    def validate_record_numbers(self, line_separator):
        csv_data = f"a{line_separator}b{line_separator}c"

        with CSVParser.parse(csv_data, CSVFormat.DEFAULT
                                    .with_record_separator(line_separator)) as parser:

            assert 0 == parser.get_record_number()
            record = parser.next_record()
            assert record is not None
            assert 1 == record.get_record_number()
            assert 1 == parser.get_record_number()
            record = parser.next_record()
            assert record is not None
            assert 2 == record.get_record_number()
            assert 2 == parser.get_record_number()
            record = parser.next_record()
            assert record is not None
            assert 3 == record.get_record_number()
            assert 3 == parser.get_record_number()
            record = parser.next_record()
            assert record is None
            assert 3 == parser.get_record_number()

    def validate_record_position(self, line_separator):
        nl = line_separator  # used as linebreak in values for better distinction

        code = (f"a,b,c{line_separator}1,2,3{line_separator}" + \
            # to see if recordPosition correctly points to the enclosing quote
            f"'A{nl}A','B{nl}B',CC{line_separator}" + \
            # unicode test... not very relevant while operating on strings 
            # instead of bytes, but for completeness...
            f"\u00c4,\u00d6,\u00dc{line_separator}EOF,EOF,EOF")

        format = (CSVFormat.new_format(',')
                        .with_quote("'")
                        .with_record_separator(line_separator))

        parser = CSVParser.parse(code, format)

        assert 0 == parser.get_record_number()

        record = parser.next_record()
        assert record is not None
        assert 1 == record.get_record_number()
        assert code.index('a') == record.get_character_position()

        record = parser.next_record()
        assert record is not None
        assert 2 == record.get_record_number()
        assert code.index('1') == record.get_character_position()

        record = parser.next_record()
        assert record is not None
        position_record3 = record.get_character_position()
        assert 3 == record.get_record_number()
        assert code.index("'A") == record.get_character_position()
        assert "A" + line_separator + "A" == record.get(0)
        assert "B" + line_separator + "B" == record.get(1)
        assert "CC" == record.get(2)

        record = parser.next_record()
        assert record is not None
        assert 4 == record.get_record_number()
        assert code.index('\u00c4') == record.get_character_position()

        record = parser.next_record()
        assert record is not None
        assert 5 == record.get_record_number()
        assert code.index("EOF") == record.get_character_position()

        parser.close()

        # now try to read starting at record 3
        parser = CSVParser(io.StringIO(code[int(position_record3):]), format, position_record3, 3)

        record = parser.next_record()
        assert record is not None
        assert 3 == record.get_record_number()
        assert code.index("'A") == record.get_character_position()
        assert "A" + line_separator + "A" == record.get(0)
        assert "B" + line_separator + "B" == record.get(1)
        assert "CC" == record.get(2)

        record = parser.next_record()
        assert record is not None
        assert 4 == record.get_record_number()
        assert code.index('\u00c4') == record.get_character_position()
        assert "\u00c4" == record.get(0)

        parser.close()
