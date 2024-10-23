from main.python.command_line_parser import CommandLineParser
from main.python.command_line import CommandLine
from main.python.options import Options
from main.python.option import Option
from main.python.util import Util
from main.python.missing_option_exception import MissingOptionException
from main.python.missing_argument_exception import MissingArgumentException
from main.python.unrecognized_option_exception import UnrecognizedOptionException
from main.python.java_handler import java_handler

class ExtendableIterator:
    def __init__(self, iterator: iter, iter_index: int = 0):
        self.iterator = list(iterator)
        self.iterator_index = iter_index

@java_handler
class Parser(CommandLineParser):
    """
    Parser creates CommandLines.
    """
    def __init__(self):
        self.cmd = CommandLine()
        self.options = Options()
        self.required_options = []

    def check_required_options(self):
        """
        Throws a MissingOptionException if all of the required options are not present.
        :raises MissingOptionException: if any of the required Options are not present.
        """
        # if there are required options that have not been processed
        if len(self.get_required_options()) != 0:
            raise MissingOptionException(self.get_required_options())
    
    def flatten(self, options: Options, arguments: list[str], stop_at_non_option: bool):
        from main.python.posix_parser import PosixParser
        return PosixParser().flatten(options, arguments, stop_at_non_option)

    def get_options(self):
        return self.options
    
    def get_required_options(self):
        return self.required_options
    
    def parse(self, options: Options, arguments: list[str], *args):
        """
        Parse the arguments according to the specified options and properties.
        :param options: the specified Options
        :param arguments: the command line arguments
        :param properties: command line option name-value pairs
        :param stop_at_non_option: if True an unrecognized argument stops the parsing and the remaining arguments are added to the CommandLine's args list. If False an unrecognized argument triggers a ParseException.
        :return: the list of atomic option and value tokens
        :raises ParseException: if there are any problems encountered while parsing the command line tokens.
        """
        if len(args) == 0:
            # (properties, stop_at_non_option) = (None, False)
            return self._parse(options, arguments, None, False)
        elif len(args) == 1:
            if isinstance(args[0], bool):
                # (properties, stop_at_non_option) = (None, args[0])
                return self._parse(options, arguments, None, *args)
            elif isinstance(args[0], dict):
                # (properties, stop_at_non_option) = (args[0], False)
                return self._parse(options, arguments, *args, False)
        elif len(args) == 2:
            # (properties, stop_at_non_option) = (args[0], args[1])
            return self._parse(options, arguments, *args)

    def _parse(self, options: Options, arguments: list[str], properties: dict, stop_at_non_option: bool):
        # clear out the data in options in case it's been used before (CLI-71)
        for opt in options.help_options():
            opt.clear_values()
        
        # clear the data from the groups
        for group in options.get_option_groups():
            group.set_selected(None)

        # initialize members
        self.set_options(options)

        self.cmd = CommandLine()

        eat_the_rest = False

        if arguments is None:
            arguments = []

        token_list: list[str] = self.flatten(options, arguments, stop_at_non_option)

        iterator = iter(token_list)
        i = 0

        # process each flattened token
        while True:
            try:
                t = next(iterator)
                i += 1
            except StopIteration:
                break

            # the value is the double-dash
            if t == "--":
                eat_the_rest = True

            # the value is a single dash
            elif t == "-":
                if stop_at_non_option:
                    eat_the_rest = True
                else:
                    self.cmd.add_arg(t)

            # the value is an option
            elif t.startswith("-"):
                if stop_at_non_option and not self.get_options().has_option(t):
                    eat_the_rest = True
                    self.cmd.add_arg(t)
                else:
                    iterator = ExtendableIterator(iterator, i)
                    self.process_option(t, iterator, token_list, i)
                    i = iterator.iterator_index
                    iterator = iter(iterator.iterator)

            # the value is an argument
            else:
                self.cmd.add_arg(t)

                if stop_at_non_option:
                    eat_the_rest = True

            # eat the remaining tokens
            if eat_the_rest:
                while True:
                    try:
                        string = next(iterator)
                        i += 1
                    except StopIteration:
                        break

                    # ensure only one double-dash is added
                    if string != "--":
                        self.cmd.add_arg(string)

        self.process_properties(properties)
        self.check_required_options()

        return self.cmd
    
    def process_args(self, opt: Option, iterator: ExtendableIterator, iteratedList: list, iter_index: int):
        """
        Process the argument values for the specified Option opt using the values retrieved from the specified iterator.
        :param opt: The current Option
        :param iter: The iterator over the flattened command line Options.
        :raises ParseException: if an argument value is required and it is has not been found.
        """
        i = iter_index

        # loop until an option is found
        while i < len(iteratedList):
            string = iteratedList[i]
            i += 1

            # found an Option, not an argument
            if self.get_options().has_option(string) and string.startswith("-"):
                i -= 1
                break

            # found a value
            try:
                opt.add_value_for_processing(Util.strip_leading_and_trailing_quotes(string))
            except:
                i -= 1
                break

        if not opt.get_values() and not opt.has_optional_arg():
            raise MissingArgumentException(opt)

        iterator.iterator = iteratedList[i:]
        iterator.iterator_index = i

    def process_option(self, arg: str, iterator: ExtendableIterator, iter_complete_list: list, iter_index: int):
        """
        Process the Option specified by arg using the values retrieved from the specified iterator iter.
        :param arg: The String value representing an Option
        :param iter: The iterator over the flattened command line arguments.
        :raises ParseException: if arg does not represent an Option
        """
        has_option = self.get_options().has_option(arg)

        # if there is no option throw a UnrecognizedOptionException
        if not has_option:
            raise UnrecognizedOptionException("Unrecognized option: " + arg, arg)
        
        # get the option represented by arg
        opt = self.get_options().get_option(arg).clone()

        # update the required options and groups
        self.update_required_options(opt)

        # if the option takes an argument value
        if opt.has_arg():
            self.process_args(opt, iterator, iter_complete_list, iter_index)

        # set the option on the command line
        self.cmd.add_option(opt)

    def process_properties(self, properties: dict):
        """
        Sets the values of Options using the values in properties.
        
        :param properties: The value properties to be processed.
        :raises ParseException: if there are any problems encountered while processing the properties.
        """
        if not properties:
            return
        
        for option, value in properties.items():
            opt = self.options.get_option(option)

            if not opt:
                raise UnrecognizedOptionException("Default option wasn't defined", option)
            
            # if the option is part of a group, check if another option of the group has been selected
            group = self.options.get_option_group(opt)
            selected = group and group.get_selected()

            if not self.cmd.has_option(option) and not selected:
                # get the value from the properties instance
                value = properties.get(option)

                if opt.has_arg():
                    if not opt.get_values() or len(opt.get_values()) == 0:
                        try:
                            opt.add_value_for_processing(value)
                        except RuntimeError:
                            # if we cannot add the value don't worry about it
                            pass
                elif value.lower() not in ["yes", "true", "1"]:
                    # if the value is not yes, true or 1 then don't add the option to the CommandLine
                    continue

                self.cmd.add_option(opt)
                self.update_required_options(opt)

    def set_options(self, options: Options):
        self.options = options
        self.required_options = options.get_required_options().copy()

    def update_required_options(self, opt: Option):
        """
        Removes the option or its group from the list of expected elements.
        :param opt: The Option being processed.
        """
        # if the option is a required option remove the option from
        # the required_options list
        if opt.is_required():
            self.get_required_options().remove(opt.get_key())
        
        # if the option is in an OptionGroup make that option the selected
        # option of the group
        if self.get_options().get_option_group(opt):
            group = self.get_options().get_option_group(opt)

            if group.is_required():
                self.required_options = [opt for opt in self.get_required_options() if opt != group]
            
            group.set_selected(opt)
