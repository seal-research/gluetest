import os
import gzip
import tempfile
import time
import platform
import sys
import io
from typing import Iterable
import pytest
from main.python.csv_parser import CSVParser
from main.python.csv_format import CSVFormat
from main.python.csv_record import CSVRecord
from main.python.lexer import Lexer
from main.python.token import Token
from main.python.extended_buffered_reader import ExtendedBufferedReader


class TestPerformance:
    __test__ = False
    max_it = 10
    num = 0
    elapsed_times = [0] * max_it
    formatter = CSVFormat.EXCEL

    class Stats:
        def __init__(self, count, fields):
            self.count = count
            self.fields = fields

    BIG_FILE = os.path.join(tempfile.gettempdir(), "worldcitiespop.txt")

    PROPS = [
        "python_version",
        "python_implementation",
        "platform",
        "system",
        "machine",
        "release",
    ]

    def get_property(self, prop_name):
        return getattr(platform, prop_name)()

    def main(self):
        if os.path.exists(self.BIG_FILE):
            print(f"Found test fixture {self.BIG_FILE}: "
                  f"{os.path.getsize(self.BIG_FILE):,d} bytes.")

        else:
            print(f"Decompressing test fixture {self.BIG_FILE}...")
            with gzip.open(
                    "src/test/resources/perf/worldcitiespop.txt.gz", 'rb'
            ) as input_file, \
                    open(self.BIG_FILE, 'wb') as output_file:
                output_file.write(input_file.read())
            print(f"Decompressed test fixture {self.BIG_FILE}: "
                  f"{os.path.getsize(self.BIG_FILE):,d} bytes.")

        args = sys.argv[1:]
        argc = len(args)
        tests = []
        if argc > 0:
            max_val = int(args[0])
        else:
            max_val = None
        if argc > 1:
            tests = args[1:]
        else:
            tests = [
                "file", "split", "extb", "exts", "csv", "lexreset", "lexnew"
            ]

        for p in self.PROPS:
            print(f"{p}={self.get_property(p)}")

        print(f"Max count: {max_val}\n")

        for test in tests:
            if "file" == test:
                self.test_read_big_file(False)
            elif "split" == test:
                self.test_read_big_file(True)
            elif "csv" == test:
                self.test_parse_commons_csv()
            elif "lexreset" == test:
                self.test_csv_lexer(False, test)
            elif "lexnew" == test:
                self.test_csv_lexer(True, test)
            elif test.startswith("CSVLexer"):
                self.test_csv_lexer(False, test)
            elif "extb" == test:
                self.test_extended_buffer(False)
            elif "exts" == test:
                self.test_extended_buffer(True)
            else:
                print(f"Invalid test name: {test}")

    @classmethod
    def teardown_class(cls):
        cls.num = 0

    @staticmethod
    def _create_temp_file():
        fd, path = tempfile.mkstemp()
        os.close(fd)
        return path

    def test_read_big_file(self, split=False):
        for i in range(self.max_it):
            start_time = self._current_millis()
            stats = self.read_all(split)
            self._show("file+split" if split else "file", stats, start_time)
        self._show_average()

    def read_all(self, split):
        count = 0
        fields = 0
        with self.create_reader() as in_file:
            for record in in_file:
                count += 1
                fields += len(record.split(",")) if split else 1
        return self.Stats(count, fields)

    @staticmethod
    def _current_millis():
        return int(round(time.time() * 1000))

    @classmethod
    def create_reader(cls):
        return io.TextIOWrapper(open(cls.BIG_FILE, 'r'))

    @staticmethod
    def _show(self, msg, stats, start_time):
        elapsed = self._current_millis() - start_time
        print(f"{msg:20}: {elapsed}ms {stats.count} lines "
              f"{stats.fields} fields")
        self.elapsed_times[self.num] = elapsed
        self.num += 1

    def _show_average(self):
        total = sum(self.elapsed_times[1:self.num]) if self.num > 1 else 0
        if self.num > 1:
            average = total // (self.num - 1)
            print(f"{'Average(not first)':20}: {average}ms")
        self.num = 0

    def test_extended_buffer(self, make_string: bool):
        for i in range(self.max_it):
            fields = 0
            lines = 0
            start_time = self._current_millis()
            with ExtendedBufferedReader(self.create_reader()) as in_file:
                if make_string:
                    read = in_file.read()
                    if read == -1:
                        break
                    if read == ord(','):
                        fields += 1
                    elif read == ord('\n'):
                        fields += 1
                        lines += 1
            fields += lines
            self._show(
                f"Extended{' toString' if make_string else ''}",
                self.Stats(lines, fields),
                start_time
            )
        self._show_average()

    def test_parse_commons_csv(self):
        for i in range(self.max_it):
            start_time = self._current_millis()
            stats = self.iterate(self.create_csv_parser())
            self._show("CSV", stats, start_time)
        self._show_average()

    def create_csv_parser(self):
        return CSVParser(self.create_reader(), self.formatter)

    def get_lexer_ctor(self, clazz: str):
        module_name = "org.apache.commons.csv." + clazz
        module = __import__(module_name)
        lexer_class = getattr(module, "Lexer")
        constructor = lexer_class.__init__
        return constructor

    def test_csv_lexer(self, new_token: bool, test: str):
        token = Token()
        dynamic = ""
        for i in range(self.max_it):
            simple_name = ""
            stats = None
            start_time = self._current_millis()
            with ExtendedBufferedReader(
                    self.create_reader()
            ) as input_file:
                lexer = self.create_test_csv_lexer(test, input_file)
                if test.startswith("CSVLexer"):
                    dynamic = "!"
                simple_name = lexer.__class__.__name__
                count = 0
                fields = 0
                while True:
                    if token.type == Token.Type.EOF:
                        break
                    if new_token:
                        token = Token()
                    else:
                        token.reset()
                    lexer.next_token(token)
                    if token.type == Token.Type.EOF:
                        break
                    if token.type == Token.Type.EORECORD:
                        fields += 1
                        count += 1
                    elif token.type == Token.Type.INVALID:
                        raise Exception(
                            f"invalid parse sequence <{token.content}>"
                        )
                    elif token.type == Token.Type.TOKEN:
                        fields += 1
                    elif token.type == Token.Type.COMMENT:
                        pass  # not really expecting these
                    else:
                        raise Exception(
                            f"Unexpected Token type: {token.type}"
                        )
                stats = self.Stats(count, fields)
            self._show(
                f"{simple_name}{dynamic} "
                f"{'new' if new_token else 'reset'}",
                stats, start_time
                )
        self._show_average()

    @staticmethod
    def create_test_csv_lexer(
        test: str, input_file: ExtendedBufferedReader
    ):
        if test.startswith("CSVLexer"):
            return (
                TestPerformance
                .get_lexer_ctor(test)
                (TestPerformance.formatter, input_file)
                )
        return Lexer(TestPerformance.formatter, input_file)

    @staticmethod
    def iterate(self, it: Iterable[CSVRecord]):
        count = 0
        fields = 0
        for record in it:
            count += 1
            fields += len(record)
        return self.Stats(count, fields)
