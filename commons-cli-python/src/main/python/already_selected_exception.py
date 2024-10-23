from main.python.parse_exception import ParseException
from main.python.option_group import OptionGroup
from main.python.option import Option
from main.python.java_handler import java_handler

@java_handler
class AlreadySelectedException(ParseException):
    """
    Thrown when more than one option in an option group has been provided.
    """

    def __init__(self, *args):
        """
        Construct a new AlreadySelectedException instance with the specified detail message.

        :param group: The option group already selected.
        :param option: The option that triggered the exception.
        :param message: The detail message.
        """
        if len(args) == 1:
            # (message, group, option) = (args[0], None, None)
            self._init(*args, None, None)
        elif len(args) == 2:
            # (message, group, option) = (msg, args[0], args[1])
            msg = f"The option '{args[1].get_key()}' was specified but an option from this group has already been selected: '{args[0].get_selected()}'"
            self._init(msg, *args)
        elif len(args) == 3:
            # (message, group, option) = args
            self._init(*args)

    def _init(self, message: str, group: OptionGroup, option: Option):
        super().__init__(message)
        self.group = group
        self.option = option

    def get_option(self):
        """
        Gets the option that was added to the group and triggered the exception.
        """
        return self.option

    def get_option_group(self):
        """
        Gets the option group where another option has been selected.
        """
        return self.group
