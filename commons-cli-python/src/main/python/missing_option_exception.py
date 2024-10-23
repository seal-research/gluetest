from main.python.parse_exception import ParseException

class MissingOptionException(ParseException):
    """
    Thrown when a required option has not been provided.
    """

    def __init__(self, missing_options):
        if type(missing_options) == str:
            super().__init__(missing_options)
        else:
            self.missing_options = missing_options
            self.__init__(self._create_message(missing_options))

    @staticmethod
    def _create_message(missing_options):
        buf = "Missing required option"
        if len(missing_options) > 1:
            buf += "s"
        buf += ": "
        buf += ", ".join(map(str, missing_options))
        return buf

    def get_missing_options(self):
        """
        Returns the list of options or option groups missing in the command line parsed.
        """
        return self.missing_options
