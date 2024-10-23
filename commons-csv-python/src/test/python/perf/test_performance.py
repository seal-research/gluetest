import pytest
import os
import gzip
from pathlib import Path
import time
import tempfile
from main.python.csv_format import CSVFormat


class TestPerformance:
    __test__ = False
    max_repeats = 10
    BIG_FILE = Path(tempfile.gettempdir()) / "worldcitiespop.txt"

    @pytest.fixture(autouse=True)
    def set_up_class(self):
        if os.path.exists(self.BIG_FILE):
            print(f"Found test fixture {self.BIG_FILE}: {os.path.getsize(self.BIG_FILE):,} bytes.")
            return

        print(f"Decompressing test fixture {self.BIG_FILE}...")
        with gzip.open("src/test/resources/perf/worldcitiespop.txt.gz", "rb") as f_in, \
                open(self.BIG_FILE, "w") as f_out:
            f_out.write(f_in.read().decode("latin-1"))

        print(f"Decompressed test fixture {self.BIG_FILE}: {os.path.getsize(self.BIG_FILE):,} bytes.")

    def create_buffered_reader(self):
        return open(self.BIG_FILE, "r", encoding="utf-8")

    def parse(self, in_stream, traverse_columns: bool):
        csv_format = CSVFormat.DEFAULT.with_ignore_surrounding_spaces(False)
        record_count = 0

        for record in csv_format.parse(in_stream):
            record_count += 1
            if traverse_columns:
                for _ in record:
                    pass  # Do nothing for now

        return record_count

    def read_all(self, in_stream):
        count = sum(1 for line in in_stream)
        return count

    def _test_parse_big_file(self, traverse_columns: bool):
        start_time = time.time()
        with self.create_buffered_reader() as in_stream:
            count = self.parse(in_stream, traverse_columns)

        total_time = time.time() - start_time
        print(f"File parsed in {total_time * 1000:.0f} milliseconds with Commons CSV: {count} lines.")
        return total_time

    def test_parse_big_file_repeat(self):
        best_time = (2**63) - 1

        for _ in range(self.max_repeats):
            best_time = min(self._test_parse_big_file(False), best_time)

        print(f"Best time out of {self.max_repeats:,} is {best_time * 1000:.0f} milliseconds.")

    def test_read_big_file(self):
        best_time = (2**63) - 1

        for _ in range(self.max_repeats):
            with self.create_buffered_reader() as in_stream:
                start_time = time.time()
                count = self.read_all(in_stream)
                total_time = time.time() - start_time

            best_time = min(total_time, best_time)
            print(f"File read in {total_time * 1000:.0f} milliseconds: {count} lines.")

        print(f"Best time out of {self.max_repeats:,} is {best_time * 1000:.0f} milliseconds.")
