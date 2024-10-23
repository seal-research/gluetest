from enum import Enum
import sys
import pytest
from io import StringIO
from main.python.csv_record import CSVRecord
from main.python.csv_printer import CSVPrinter
from main.python.csv_format import CSVFormat
from main.python.csv_parser import CSVParser


class TestCSVRecord:

    class EnumFixture(Enum):
        UNKNOWN_COLUMN = 0

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.values = ["A", "B", "C"]
        self.record = CSVRecord(
            self.values, None, None, 0, -1
        )
        self.header = {
            "first": 0,
            "second": 1,
            "third": 2
        }
        self.record_with_header = CSVRecord(
            self.values, self.header, None, 0, -1
        )

    def test_get_int(self):
        assert self.values[0] == self.record.get(0)
        assert self.values[1] == self.record.get(1)
        assert self.values[2] == self.record.get(2)

    def test_get_string(self):
        assert self.values[0] == self.record_with_header.get("first")
        assert self.values[1] == self.record_with_header.get("second")
        assert self.values[2] == self.record_with_header.get("third")

    def test_get_string_inconsistent_record(self):
        self.header["fourth"] = 4
        with pytest.raises(ValueError):
            self.record_with_header.get("fourth")

    def test_get_string_no_header(self):
        with pytest.raises(ValueError):
            self.record.get("first")

    def test_get_unmapped_enum(self):
        with pytest.raises(ValueError):
            assert (
                self.record_with_header.get(self.EnumFixture.UNKNOWN_COLUMN)
                is None
            )

    def test_get_unmapped_name(self):
        with pytest.raises(ValueError):
            assert self.record_with_header.get("fourth") is None

    def test_get_unmapped_negative_int(self):
        with pytest.raises(IndexError):
            assert self.record_with_header.get(-sys.maxsize - 1) is None

    def test_get_unmapped_positive_int(self):
        with pytest.raises(IndexError):
            assert self.record_with_header.get(sys.maxsize) is None

    def test_is_consistent(self):
        assert self.record.is_consistent()
        assert self.record_with_header.is_consistent()

        self.header["fourth"] = 4
        assert not self.record_with_header.is_consistent()

    def test_is_mapped(self):
        assert not self.record.is_mapped("first")
        assert self.record_with_header.is_mapped("first")
        assert not self.record_with_header.is_mapped("fourth")

    def test_is_set(self):
        assert not self.record.is_set("first")
        assert self.record_with_header.is_set("first")
        assert not self.record_with_header.is_set("fourth")

    def test_iterator(self):
        i = 0
        for value in self.record:
            assert value == self.values[i]
            i += 1

    def test_put_in_map(self):
        map = {}
        self.record_with_header.put_in(map)
        self.validate_map(map, False)
        map2 = self.record_with_header.put_in({})
        self.validate_map(map2, False)

    def test_remove_and_add_columns(self):
        with CSVPrinter(StringIO(), CSVFormat.DEFAULT) as printer:
            map = self.record_with_header.to_map()
            map.pop("OldColumn", None)
            map['ZColumn'] = 'NewValue'
            
            values = list(map.values())
            values.sort()
            printer.print_record(values)
            assert printer.get_out().getvalue() == "A,B,C,NewValue" + CSVFormat.DEFAULT.get_record_separator()

    def test_to_map(self):
        map = self.record_with_header.to_map()
        self.validate_map(map, True)

    def test_to_map_with_short_record(self):
        with CSVParser.parse("a,b", CSVFormat.DEFAULT.with_header("A", "B", "C")) as parser:
            short_rec = next(parser.iterator())
            short_rec.to_map()

    def test_to_map_with_no_header(self):
        with CSVParser.parse("a,b", CSVFormat.new_format(',')) as parser:
            short_rec = next(parser.iterator())
            map = short_rec.to_map()
        assert map is not None, "Map is not null."
        assert not map.keys(), "Map is empty."

    def validate_map(self, map, allows_nulls):
        assert "first" in map
        assert "second" in map
        assert "third" in map
        assert "fourth" not in map

        if allows_nulls:
            assert None not in map

        assert map.get("first") == "A"
        assert map.get("second") == "B"
        assert map.get("third") == "C"
        assert map.get("fourth") is None
