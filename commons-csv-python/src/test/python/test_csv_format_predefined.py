import pytest
from main.python.csv_format import CSVFormat


class TestCSVFormatPredefined:

    def _test(self, format: CSVFormat, enum_name: str):
        assert (CSVFormat.Predefined.value_of(enum_name)
                .get_format() == format)
        assert CSVFormat.value_of(enum_name) == format

    def test_default(self):
        self._test(CSVFormat.DEFAULT, "Default")

    def test_excel(self):
        self._test(CSVFormat.EXCEL, "Excel")

    def test_mysql(self):
        self._test(CSVFormat.MYSQL, "MySQL")

    def test_oracle(self):
        self._test(CSVFormat.ORACLE, "Oracle")

    def test_postgresql_csv(self):
        self._test(
            CSVFormat.POSTGRESQL_CSV, "PostgreSQLCsv"
        )

    def test_postgresql_text(self):
        self._test(
            CSVFormat.POSTGRESQL_TEXT, "PostgreSQLText"
        )

    def test_rfc4180(self):
        self._test(CSVFormat.RFC4180, "RFC4180")

    def test_tdf(self):
        self._test(CSVFormat.TDF, "TDF")
