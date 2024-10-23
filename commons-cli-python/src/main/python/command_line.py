from main.python.option import Option
from main.python.type_handler import TypeHandler
from main.python.util import Util
from main.python.parse_exception import ParseException
import sys
from main.python.java_handler import java_handler, isinstance

@java_handler
class CommandLine:
    """
    Represents list of arguments parsed against a Options descriptor.

    It allows querying of a boolean has_option(opt: str), in addition to retrieving the
    get_option_value(opt: str) for options requiring arguments.

    Additionally, any left-over or unrecognized arguments, are available for further processing.
    """
    class Builder:

        def __init__(self):
            """
            CommandLine that is being build by this Builder.
            """
            self.command_line = CommandLine()

        def add_arg(self, arg: str):
            """
            Add left-over unrecognized option/argument.

            :param arg: the unrecognized option/argument.
            :return: this Builder instance for method chaining.
            """
            self.command_line.add_arg(arg)
            return self

        def add_option(self, opt: Option):
            """
            Add an option to the command line. The values of the option are stored.

            :param opt: the processed option.
            :return: this Builder instance for method chaining.
            """
            self.command_line.add_option(opt)
            return self

        def build(self):
            return self.command_line

    def __init__(self):
        # The serial version UID.
        self.serial_version_uid = 1

        # The unrecognized options/arguments
        self.args = []

        # The processed options
        self.options: list[Option] = []

    def add_arg(self, arg: str):
        """
        Add left-over unrecognized option/argument.

        :param arg: the unrecognized option/argument.
        """
        self.args.append(arg)

    def add_option(self, opt: Option):
        """
        Add an option to the command line. The values of the option are stored.

        :param opt: the processed option.
        """
        self.options.append(opt)

    def get_arg_list(self):
        """
        Retrieve any left-over non-recognized options and arguments

        :return: remaining items passed in but not parsed as a List.
        """
        return self.args
    
    def get_args(self):
        """
        Retrieve any left-over non-recognized options and arguments

        :return: remaining items passed in but not parsed as an array.
        """
        return self.args
    
    def get_option_object(self, opt: str):
        """
        Return the Object type of this Option.
        
        :param opt: the name of the option.
        :return: the type of this Option.

        Deprecated. Use get_option_properties(opt: str) instead.
        """
        try:
            return self.get_parsed_option_value(opt)
        except ParseException as pe:
            sys.stderr.write(f"Exception found converting {opt} to desired type: {pe}\n")
            return None

    def get_option_properties(self, arg):
        if isinstance(arg, Option):
            option = arg
            """
            Retrieve the map of values associated to the option. This is convenient for options specifying Java properties like
            -Dparam1=value1
            -Dparam2=value2. The first argument of the option is the key, and the 2nd argument is the value. If the option
            has only one argument (-Dfoo) it is considered as a boolean flag and the value is "true".

            :param option: name of the option.
            :return: The Properties mapped by the option, never None even if the option doesn't exists.
            """
            props = {}

            for processed_option in self.options:
                if processed_option.equals(option):
                    values = processed_option.get_values_list()
                    if len(values) >= 2:
                        # use the first 2 arguments as the key/value pair
                        props[values[0]] = values[1]
                    elif len(values) == 1:
                        # no explicit value, handle it as a boolean
                        props[values[0]] = "true"

            return props
        
        if isinstance(arg, str):
            opt = arg
            """
            Retrieve the map of values associated to the option. This is convenient for options specifying Java properties like
            -Dparam1=value1
            -Dparam2=value2. The first argument of the option is the key, and the 2nd argument is the value. If the option
            has only one argument (-Dfoo) it is considered as a boolean flag and the value is "true".

            :param opt: name of the option.
            :return: The Properties mapped by the option, never None even if the option doesn't exists.
            """
            props = {}

            for option in self.options:
                if opt == option.get_opt() or opt == option.get_long_opt():
                    values = option.get_values_list()
                    if len(values) >= 2:
                        # use the first 2 arguments as the key/value pair
                        props[values[0]] = values[1]
                    elif len(values) == 1:
                        # no explicit value, handle it as a boolean
                        props[values[0]] = "true"

            return props
        
    def get_options(self):
        """
        Gets an array of the processed Options.

        :return: an array of the processed Options.
        """
        return self.options

    def get_option_value(self, arg1 = None, arg2 = None):
        if arg2 is None:
            if isinstance(arg1, str):
                opt = arg1
                """
                Retrieve the first argument, if any, of this option.

                :param opt: the name of the option.
                :return: Value of the argument if option is set, and has an argument, otherwise None.
                """
                return self.get_option_value(self.resolve_option(opt))
            
            if isinstance(arg1, Option):
                option = arg1
                """
                Retrieve the first argument, if any, of this option.

                :param option: the name of the option.
                :return: Value of the argument if option is set, and has an argument, otherwise None.
                """
                if option is None:
                    return None
                values = self.get_option_values(option)
                return None if values is None else values[0]
        else:
            if isinstance(arg1, str):
                opt = arg1
                default_value = arg2
                """
                Retrieve the first argument, if any, of an option.

                :param opt: name of the option.
                :param default_value: is the default value to be returned if the option is not specified.
                :return: Value of the argument if option is set, and has an argument, otherwise default_value.
                """
                return self.get_option_value(self.resolve_option(opt), default_value)
            
            if isinstance(arg1, Option):
                option = arg1
                default_value = arg2
                """
                Retrieve the first argument, if any, of an option.

                :param option: name of the option.
                :param default_value: is the default value to be returned if the option is not specified.
                :return: Value of the argument if option is set, and has an argument, otherwise default_value.
                """
                answer = self.get_option_value(option)
                return answer if answer is not None else default_value
            
    def get_option_values(self, arg):
        if isinstance(arg, str):
            opt = arg
            """
            Retrieves the array of values, if any, of an option.

            :param opt: string name of the option.
            :return: Values of the argument if option is set, and has an argument, otherwise None.
            """
            return self.get_option_values(self.resolve_option(opt))
        
        if isinstance(arg, Option):
            option = arg
            """
            Retrieves the array of values, if any, of an option.

            :param option: string name of the option.
            :return: Values of the argument if option is set, and has an argument, otherwise None.
            """
            values = []
            for processed_option in self.options:
                if processed_option.equals(option):
                    values.extend(processed_option.get_values_list())
            return None if len(values) == 0 else values

    def get_parsed_option_value(self, arg):
        if isinstance(arg, str):
            opt = arg
            """
            Return a version of this Option converted to a particular type.

            :param opt: the name of the option.
            :return: the value parsed into a particular object.
            :raises ParseException: if there are problems turning the option value into the desired type
            """
            return self.get_parsed_option_value(self.resolve_option(opt))
        
        if isinstance(arg, Option):
            option = arg
            """
            Return a version of this Option converted to a particular type.

            :param option: the name of the option.
            :return: the value parsed into a particular object.
            :raises ParseException: if there are problems turning the option value into the desired type
            """
            if option is None:
                return None
            res = self.get_option_value(option)
            if res is None:
                return None
            return TypeHandler.create_value(res, option.get_type())

    def has_option(self, arg):
        if isinstance(arg, str):
            opt = arg
            """
            Tests to see if an option has been set.

            :param opt: the option to check.
            :return: true if set, false if not.
            """
            return self.has_option(self.resolve_option(opt))
        
        if isinstance(arg, Option):
            option = arg
            """
            Tests to see if an option has been set.

            :param option: the option to check.
            :return: true if set, false if not.
            """
            for o in self.options:
                if o.equals(option):
                    return True

        return False
        
    def iterator(self):
        """
        Returns an iterator over the Option members of CommandLine.

        :return: an Iterator over the processed Option members of this CommandLine.
        """
        return iter(self.options)
    
    def resolve_option(self, opt: str):
        """
        Retrieves the option object given the long or short option as a String

        :param opt: short or long name of the option.
        :return: Canonicalized option.
        """
        opt = Util.strip_leading_hyphens(opt)
        for option in self.options:
            if opt == option.get_opt() or opt == option.get_long_opt():
                return option
        return None
