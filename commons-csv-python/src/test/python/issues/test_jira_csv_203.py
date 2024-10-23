import pytest
from main.python.csv_printer import CSVPrinter
from main.python.csv_format import CSVFormat
from main.python.quote_mode import QuoteMode
from io import StringIO


class TestJiraCsv203:

    def test_quote_mode_all(self):
        format = CSVFormat.EXCEL \
            .with_null_string("N/A") \
            .with_ignore_surrounding_spaces(True) \
            .with_quote_mode(QuoteMode.ALL)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record([None, "Hello", None, "World"])

        assert buffer.getvalue() == "\"N/A\",\"Hello\",\"N/A\",\"World\"\r\n"

    def test_quote_mode_all_non_null(self):
        format = CSVFormat.EXCEL \
            .with_null_string("N/A") \
            .with_ignore_surrounding_spaces(True) \
            .with_quote_mode(QuoteMode.ALL_NON_NULL)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record([None, "Hello", None, "World"])

        assert buffer.getvalue() == "N/A,\"Hello\",N/A,\"World\"\r\n"

    def test_without_quote_mode(self):
        format = CSVFormat.EXCEL \
            .with_null_string("N/A") \
            .with_ignore_surrounding_spaces(True)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record([None, "Hello", None, "World"])

        assert buffer.getvalue() == "N/A,Hello,N/A,World\r\n"

    def test_quote_mode_minimal(self):
        format = CSVFormat.EXCEL \
            .with_null_string("N/A") \
            .with_ignore_surrounding_spaces(True) \
            .with_quote_mode(QuoteMode.MINIMAL)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record([None, "Hello", None, "World"])

        assert buffer.getvalue() == "N/A,Hello,N/A,World\r\n"

    def test_quote_mode_non_numeric(self):
        format = CSVFormat.EXCEL \
            .with_null_string("N/A") \
            .with_ignore_surrounding_spaces(True) \
            .with_quote_mode(QuoteMode.NON_NUMERIC)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record([None, "Hello", None, "World"])

        assert buffer.getvalue() == "N/A,\"Hello\",N/A,\"World\"\r\n"

    def test_without_null_string(self):
        format = CSVFormat.EXCEL \
            .with_ignore_surrounding_spaces(True) \
            .with_quote_mode(QuoteMode.ALL)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record([None, "Hello", None, "World"])

        assert buffer.getvalue() == ",\"Hello\",,\"World\"\r\n"

    def test_with_empty_values(self):
        format = CSVFormat.EXCEL \
            .with_null_string("N/A") \
            .with_ignore_surrounding_spaces(True) \
            .with_quote_mode(QuoteMode.ALL)

        buffer = StringIO()
        printer = CSVPrinter(buffer, format)
        printer.print_record(["", "Hello", "", "World"])

        assert buffer.getvalue() == "\"\",\"Hello\",\"\",\"World\"\r\n"
