import locale
import pkg_resources
import pytest
from pathlib import Path
import os
from main.python.csv_format import CSVFormat
from main.python.csv_parser import CSVParser
from main.python.csv_record import CSVRecord
from urllib.parse import urlparse


BASE = Path(__file__).parent.parent / "resources" / "CSVFileParser"

@pytest.mark.parametrize("file_name", [
    f for f in os.listdir(BASE) if f.startswith("test") and f.endswith(".txt")
])
class TestCSVFileParser:
    """
    Parse tests using test files
    """

    @pytest.fixture(autouse=True)
    def setup(self, file_name: str):
        file = Path.joinpath(BASE, file_name)
        self.test_name = file.name
        self.test_data = open(file)

    def read_test_data(self):
        line = self._readline()
        while line and line.startswith("#"):
            line = self._readline()
        return line

    def _readline(self, length=-1):
        initial_pos = self.test_data.tell()
        value = self.test_data.readline(length)

        if not value:
            return None

        offset = 0
        if value.endswith("\r\n"):
            value = value[:-2]
            offset = 2
        if value.endswith(("\r", "\n")):
            value = value[:-1]
            offset = 1
            
        min_break = len(value)
        if "\r" in value and value.index("\r") < min_break:
            min_break = value.index("\r")
            offset = 1
        if "\n" in value and value.index("\n") < min_break:
            min_break = value.index("\n")
            offset = 1
        if "\r\n" in value and value.index("\r\n") <= min_break:
            min_break = value.index("\r\n")
            offset = 2

        s = value[:min_break]
        self.test_data.seek(initial_pos + len(s) + offset)
        return s

    @staticmethod
    def _parse_bool(value: str):
        return str(value.lower() == "true").lower()
    
    def test_csv_file(self):
        line = self.read_test_data()
        assert line is not None, "file must contain config line"
        split = line.split(" ")
        assert len(split) >= 1, f"{self.test_data} require 1 param"
        format = CSVFormat.new_format(',').with_quote('"')
        check_comments = False
        for i in range(1, len(split)):
            option = split[i]
            option_parts = option.split("=", 1)
            if option_parts[0].lower() == "ignoreempty":
                format = format.with_ignore_empty_lines(self._parse_bool(option_parts[1]))
            elif option_parts[0].lower() == "ignorespaces":
                format = format.with_ignore_surrounding_spaces(self._parse_bool(option_parts[1]))
            elif option_parts[0].lower() == "commentstart":
                format = format.with_comment_marker(option_parts[1][0])
            elif option_parts[0].lower() == "checkcomments":
                check_comments = True
            else:
                pytest.fail(f"{self.test_data} unexpected option: {option}")
        line = self.read_test_data()
        assert line == str(format), f"{self.test_data} Expected format "

        with CSVParser.parse(
            Path.joinpath(BASE, split[0]), 
            locale.getpreferredencoding(), 
            format
            ) as parser:
            record: CSVRecord
            for record in parser:
                parsed = str(record.values())
                if check_comments:
                    comment = record.get_comment().replace("\n", "\\n")
                    if comment is not None:
                        parsed += "#" + comment
                count = record.size()
                t = self.read_test_data()
                assert t == f"{count}:{parsed}", self.test_name

    def test_csv_url(self):
        line = self.read_test_data()
        assert line is not None, "file must contain config line"
        split = line.split(" ")
        assert len(split) >= 1, f"{self.test_data} require 1 param"
        format = CSVFormat.new_format(',').with_quote('"')
        check_comments = False
        for i in range(1, len(split)):
            option = split[i]
            option_parts = option.split("=", 1)
            if option_parts[0].lower() == "ignoreempty":
                format = format.with_ignore_empty_lines(self._parse_bool(option_parts[1]))
            elif option_parts[0].lower() == "ignorespaces":
                format = format.with_ignore_surrounding_spaces(self._parse_bool(option_parts[1]))
            elif option_parts[0].lower() == "commentstart":
                format = format.with_comment_marker(option_parts[1][0])
            elif option_parts[0].lower() == "checkcomments":
                check_comments = True
            else:
                pytest.fail(f"{self.test_data} unexpected option: {option}")
        line = self.read_test_data()
        assert line == str(format), f"{self.test_data} Expected format "

        p = urlparse(
                Path(
                    pkg_resources.resource_filename(
                        "test", 
                        "resources/CSVFileParser/" + split[0]
                    )
                ).as_uri()
        )
        with CSVParser.parse(p, 'utf-8', format) as parser:
            record: CSVRecord
            for record in parser:
                    parsed = str(record.values())
                    if check_comments:
                        comment = record.get_comment().replace("\n", "\\n")
                        if comment is not None:
                            parsed += "#" + comment
                    count = record.size()
                    assert self.read_test_data() == f"{count}:{parsed}", self.test_data
