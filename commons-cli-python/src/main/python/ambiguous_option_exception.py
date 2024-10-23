from main.python.unrecognized_option_exception import UnrecognizedOptionException

class AmbiguousOptionException(UnrecognizedOptionException):
    """
    Exception thrown when an option can't be identified from a partial name.
    """
    def __init__(self, option, matching_options):
        self.matching_options = matching_options
        self.option = option
        super().__init__(self._create_message(option, matching_options), option)

    @staticmethod
    def _create_message(option, matching_options):
        buf = f"Ambiguous option: '{option}'  (could be: "
        buf += ", ".join(f"'{opt}'" for opt in matching_options)
        buf += ")"
        return buf

    def get_matching_options(self):
        """
        Gets the options matching the partial name.

        :return: a collection of options matching the name
        """
        return self.matching_options
