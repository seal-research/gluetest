from pathlib import Path
from main.python.csv_parser import CSVParser
from main.python.csv_format import CSVFormat
from io import StringIO

BASE = Path(__file__).parent.parent.parent / "resources"

class TestJiraCsv198:
    CSV_FORMAT = CSVFormat.EXCEL.with_delimiter('^').with_first_record_as_header()

    def test(self):
        points_of_reference = open(str(BASE) + "/CSV-198/optd_por_public.csv", encoding="utf-8")
        assert points_of_reference is not None
        with TestJiraCsv198.CSV_FORMAT.parse(points_of_reference) as parser:
            for record in parser:
                location_type = record.get("location_type")
                assert location_type is not None
