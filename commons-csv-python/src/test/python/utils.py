from main.python.csv_record import CSVRecord

class Utils:

    @staticmethod
    def compare(message: str, expected: list[list[str]], actual: list[CSVRecord]):
        """
        Checks if the 2d array has the same contents as the list of records.

        :param message: the message to be displayed
        :param expected: the 2d array of expected results
        :param actual: the list of records, each containing an array of values
        """
        assert len(expected) == len(actual), message + "  - outer array size"
        for i in range(len(expected)):
            assert expected[i] == actual[i].values(), message + " (entry " + str(i) + ")"
