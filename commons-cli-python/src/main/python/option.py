from main.python.option_validator import OptionValidator
from main.python.java_handler import java_handler, Types, isinstance

@java_handler
class Option:
    """
    Describes a single command-line option. It maintains information regarding the short-name of the option, the
    long-name, if any exists, a flag indicating if an argument is required for this option, and a self-documenting
    description of the option.

    An Option is not created independently, but is created through an instance of {@link Options}. An Option is required
    to have at least a short or a long-name.

    Note: once an option has been added to an instance of options, its required flag cannot be changed
    """


    class Builder:
        """
        A nested builder class to create Option instances using descriptive methods.
        """
        def __init__(self, option: str = None, long_opt: str = None,
                     desc: str = None, arg_count: int = None, required: bool = False, optional_arg: bool = False,
                        value_separator: str = '\0', arg_name: str = None, type = Types.String):
            """
            Constructs a new Builder with the minimum required parameters for an option instance.
            
            :param option: short representation of the option
            :raises ValueError: if there are any non valid Option characters in option
            """
            self.option(option)
            self.arg_count = arg_count if arg_count != None else Option.UNINITIALIZED
            self._type = type
            self.long_option = long_opt
            self._arg_name = arg_name
            self._required = required
            self._optional_arg = optional_arg
            self._value_separator = value_separator
            self.description = desc
        
        def arg_name(self, arg_name: str):
            """
            Sets the display name for the argument value.
            
            :param arg_name: the display name for the argument value.
            :return: this Builder, to allow method chaining
            """
            self._arg_name = arg_name
            return self
        
        def build(self):
            """
            Constructs an Option with the values declared by this Builder.
            
            :return: the new Option
            :raises ValueError: if neither opt or long_opt has been set
            """
            if self._option is None and self.long_option is None:
                raise ValueError("Either option or long_option must be specified")
            
            return Option(self)
        
        def desc(self, description: str):
            """
            Sets the description for this option.
            
            :param description: the description of the option.
            :return: this Builder, to allow method chaining
            """
            self.description = description
            return self
        
        def has_arg(self, has_arg = None):
            """
            Indicates that the Option will require an argument.
            
            :param has_arg: specifies whether the Option takes an argument or not
            :return: this Builder, to allow method chaining
            """
            if has_arg is not None:
                self.arg_count = 1 if has_arg else Option.UNINITIALIZED
            else:
                self.has_arg(True)
            return self
        
        def has_args(self):
            """
            Indicates if the Option can have unlimited argument values.

            :return: this Builder, to allow method chaining
            """
            self.arg_count = Option.UNLIMITED_VALUES
            return self

        def long_opt(self, long_opt: str):
            """
            Sets the long name of the Option.
            
            :param long_opt: the long name of the Option
            :return: this Builder, to allow method chaining
            """
            self.long_option = long_opt
            return self
        
        def number_of_args(self, number_of_args: int):
            """
            Sets the number of argument values the Option can take.
            
            :param number_of_args: the number of argument values
            :return: this Builder, to allow method chaining
            """
            self.arg_count = number_of_args
            return self
        
        def option(self, option: str = None):
            """
            Sets the name of the Option.
            
            :param option: the name of the Option
            :return: this Builder, to allow method chaining
            :raises ValueError: if there are any non valid Option characters in opt
            """
            self._option = OptionValidator.validate(option)
            return self
        
        def optional_arg(self, is_optional: bool):
            """
            Sets whether the Option can have an optional argument.
            
            :param is_optional: specifies whether the Option can have an optional argument.
            :return: this Builder, to allow method chaining
            """
            self._optional_arg = is_optional
            return self
        
        def required(self, required = None):
            """
            Sets whether the Option is mandatory.
            
            :param required: specifies whether the Option is mandatory
            :return: this Builder, to allow method chaining
            """
            if required is not None:
                self._required = required
            else:
                self._required = True
            return self

        def type(self, type):
            """
            Sets the type of the Option.
            
            :param type: the type of the Option
            :return: this Builder, to allow method chaining
            """
            self._type = type
            return self
        
        def value_separator(self, sep = None):
            """
            The Option will use sep as a means to separate argument values. 
            If sep is not specified, the Option will use '=' as a means to separate argument value.

            :param sep: The value separator.
            :return: this Builder, to allow method chaining
            """
            if sep is not None:
                self._value_separator = sep
            else:
                self._value_separator = '='
            return self

    # Specifies the number of argument values has not been specified
    UNINITIALIZED = -1

    # Specifies the number of argument values is infinite
    UNLIMITED_VALUES = -2
        
    def builder(option = None):
        """
        Returns a Builder to create an Option using descriptive methods.
        
        :param option: short representation of the option
        :return: a new Builder instance
        :raises ValueError: if there are any non valid Option characters in opt
        """
        return Option.Builder(option)
    
    def __init__(self, *args):
        self._init(*args)

    def _init(self, *args):
        # The number of argument values this option can have.
        self.arg_count = Option.UNINITIALIZED

        # The type of this Option.
        self.type = Types.String

        #The list of argument values.
        self.values = []

        self.valuesep = ''
        self.required = False
        self.optional_arg = False
        self.arg_name = None
    
        if len(args) == 1:
            builder: Option.Builder = args[0]
            self.arg_name = builder._arg_name
            self.description = builder.description
            self.long_option = builder.long_option
            self.arg_count = builder.arg_count
            self.option = builder._option
            self.optional_arg = builder._optional_arg
            self.required = builder._required
            self.type = builder._type
            self.valuesep = builder._value_separator
        elif len(args) == 2:
            option, description = args
            self._init(option, None, False, description)
        elif len(args) == 3:
            option, has_arg, description = args
            self._init(option, None, has_arg, description)
        elif len(args) >= 4:
            option = args[0]
            long_option = args[1]
            has_arg = args[2]
            description = args[3]
            
            # optional args set during type mapping
            num_args = args[4] if len(args) > 4 else None
            val_separator = args[5] if len(args) > 5 else None
            required = args[6] if len(args) > 6 else False
            arg_name = args[7] if len(args) > 7 else None
            optional_arg = args[8] if len(args) > 8 else False
            _type = args[9] if len(args) > 9 else Types.String
            values = args[10] if len(args) > 10 else []

            """
            Creates an Option using the specified parameters.
            
            :param option: short representation of the option
            :param long_option: the long representation of the option
            :param has_arg: specifies whether the Option takes an argument or not
            :param description: describes the function of the option
            :raises ValueError: if there are any non valid Option characters in opt
            """
            # ensure that the option is valid
            self.option = OptionValidator.validate(option)
            self.long_option = long_option

            # if has_arg is set then the number of arguments is 1
            if num_args is not None and num_args != Option.UNINITIALIZED:
                self.arg_count = num_args
            elif has_arg:
                self.arg_count = 1
            else:
                self.arg_count = Option.UNINITIALIZED

            if val_separator is not None:
                self.valuesep = val_separator

            self.required = required
            self.description = description
            self.arg_name = arg_name
            self.optional_arg = optional_arg
            self.type = _type

            self.values = values

    def accepts_arg(self):
        """
        Tells if the option can accept more arguments.
     
        :return false if the maximum number of arguments is reached
        """
        return (self.has_arg() or self.has_args() or self.has_optional_arg()) and (self.arg_count <= 0 or len(self.values) < self.arg_count)

    def add(self, value: str):
        """
        Add the value to this Option. If the number of arguments is greater than zero and there is enough space in the list
        then add the value. Otherwise, throw a runtime exception.
        
        :param value: The value to be added to this Option
        """
        if not self.accepts_arg():
            raise RuntimeError("Cannot add value, list full.")

        # store value
        self.values.append(value)

    # add_value has not been implemented as it has been deprecated
    # and is not intended to be used.

    def add_value_for_processing(self, value: str):
        """
        Adds the specified value to this Option.
        
        :param value: is a/the value of this Option
        """
        if self.arg_count == Option.UNINITIALIZED:
            raise RuntimeError("NO_ARGS_ALLOWED")
        self.process_value(value)

    def clear_values(self):
        """
        Clear the Option values. After a parse is complete, these are left with data in them and they need clearing if
        another parse is done.
        """
        self.values = []

    def clone(self):
        """
        :return: a clone of this Option instance
        """
        #
        # Note: In Java, clone() returns an Object which is not the same 
        # but has the same attributes. This has been replicated here.
        #
        option = Option()

        for attr, val in vars(self).items():
            setattr(option, attr, val)

        option.values = self.values.copy() # create a different list object
        return option
    
    def __eq__(self, obj):
        if self is obj:
            return True
        if not isinstance(obj, Option):
            return False
        return self.long_option == obj.long_option and self.option == obj.option

    def equals(self, obj):
        """
        Kept for compatibility with other classes that might use this method.
        Should eventually be removed.
        """
        return self.__eq__(obj)

    def get_arg_name(self):
        """
        Gets the display name for the argument value.

        :return: the display name for the argument value.
        """
        return self.arg_name

    def get_args(self):
        """
        Gets the number of argument values this Option can take.

        :return: num the number of argument values
        """
        return self.arg_count

    def get_description(self):
        """
        Gets the self-documenting description of this Option

        :return: The string description of this option
        """
        return self.description
    
    def get_id(self):
        """
        Gets the id of this Option. This is only set when the Option shortOpt is a single character. This is used for
        switch statements.

        :return: The id of this Option
        """
        return self.get_key()[0]

    def get_key(self):
        """
        Gets the 'unique' Option identifier.

        :return: the 'unique' Option identifier
        """
        return self.option if self.option is not None else self.long_option
    
    def get_long_opt(self):
        """
        Gets the long name of this Option.

        :return: the long name of this Option, or null if there is no long name
        """
        return self.long_option
    
    def get_opt(self):
        """
        Gets the name of this Option.

        :return: The name of this option
        """
        return self.option
    
    def get_type(self):
        """
        Gets the type of this Option.

        :return: The type of this option
        """
        return self.type

    def get_value(self, val = None):
        """
        Gets the specified value of this Option or None if there is no value.

        :return: the value/first value of this Option or None if there is no value.
        """
        if val is None:
            return None if self.has_no_values() else self.values[0]
        else:
            if type(val) == int:
                index = val
                """
                :param index: The index of the value to be returned.
                :raises IndexError: if index is less than 0 or greater than the number of the values for this Option.
                """
                #
                # Java documentation had an error here. 
                # It said that the exception was raised if index was less than 1. 
                # I have assumed that this was a typo and have not checked for it.
                #
                return None if self.has_no_values() else self.values[index]
            if type(val) == str:
                default_value = val
                """
                Gets the value/first value of this Option or the default_value if there is no value.

                :param default_value: The value to be returned if there is no value.
                :return: the value/first value of this Option or the default_value if there are no values."""
                value = self.get_value()
                return value if value is not None else default_value
        
    def get_values(self):
        """
        Gets the values of this Option as a String array or None if there are no values

        :return: the values of this Option as a String array or None if there are no values
        """
        return None if self.has_no_values() else self.values.copy()
    
    def get_value_separator(self):
        """
        Gets the value separator character.

        :return: the value separator character.
        """
        return self.valuesep
    
    def get_values_list(self):
        """
        Gets the values of this Option as a List or None if there are no values.

        :return: the values of this Option as a List or None if there are no values
        """
        return self.values
    
    def has_arg(self):
        """
        Query to see if this Option requires an argument

        :return: boolean flag indicating if an argument is required
        """
        return self.arg_count > 0 or self.arg_count == Option.UNLIMITED_VALUES
    
    def has_arg_name(self):
        """
        Returns whether the display name for the argument value has been set.

        :return: if the display name for the argument value has been set.
        """
        return self.arg_name is not None and self.arg_name != ''
    
    def has_args(self):
        """
        Query to see if this Option can take many values.

        :return: boolean flag indicating if multiple values are allowed
        """
        return self.arg_count > 1 or self.arg_count == Option.UNLIMITED_VALUES
    
    def hash_code(self):
        return hash((self.long_option, self.option))
    
    def has_long_opt(self):
        """
        Query to see if this Option has a long name

        :return: boolean flag indicating existence of a long name
        """
        return self.long_option is not None
    
    def has_no_values(self):
        """
        Returns whether this Option has any values.

        :return: whether this Option has any values.
        """
        return len(self.values) == 0
    
    def has_optional_arg(self):
        """
        :return: whether this Option can have an optional argument
        """
        return self.optional_arg
    
    def has_value_separator(self):
        """
        Return whether this Option has specified a value separator.

        :return: whether this Option has specified a value separator.
        """
        return self.valuesep != ''

    def is_required(self):
        """
        Query to see if this Option is mandatory

        :return: boolean flag indicating whether this Option is mandatory
        """
        return self.required
    
    def process_value(self, value: str):
        """
        Processes the value. If this Option has a value separator the value will have to be parsed into individual tokens.
        When n-1 tokens have been processed and there are more value separators in the value, parsing is ceased and the
        remaining characters are added as a single token.

        :param value: The String to be processed.
        """
        # this Option has a separator character
        if self.has_value_separator():
            # get the separator character
            sep = self.get_value_separator()
            # store the index for the value separator
            index = value.find(sep)

            # while there are more value separators
            while index != -1:
                # next value to be added
                if len(self.values) == self.arg_count - 1:
                    break

                # store
                self.add(value[:index])

                # parse
                value = value[index + 1:]

                # get new index
                index = value.find(sep)

        # store the actual value or the last value that has been parsed
        self.add(value)

    def requires_arg(self):
        """
        Tells if the option requires more arguments to be valid.

        :return: false if the option doesn't require more arguments
        """
        if self.optional_arg:
            return False
        if self.arg_count == Option.UNLIMITED_VALUES:
            return len(self.values) == 0 
        return self.accepts_arg()
    
    def set_arg_name(self, arg_name: str):
        """
        Sets the display name for the argument value.

        :param arg_name: the display name for the argument value.
        """
        self.arg_name = arg_name

    def set_args(self, num: int):
        """
        Sets the number of argument values this Option can take.

        :param num: the number of argument values
        """
        self.arg_count = num

    def set_description(self, description: str):
        """
        Sets the self-documenting description of this Option

        :param description: The description of this option
        """
        self.description = description

    def set_long_opt(self, long_opt: str):
        """
        Sets the long name of this Option.

        :param long_opt: the long name of this Option
        """
        self.long_option = long_opt

    def set_optional_arg(self, optional_arg: bool):
        """
        Sets whether this Option can have an optional argument.

        :param optional_arg: specifies whether the Option can have an optional argument.
        """
        self.optional_arg = optional_arg

    def set_required(self, required: bool):
        """
        Sets whether this Option is mandatory.

        :param required: specifies whether this Option is mandatory
        """
        self.required = required
    
    def set_type(self, type):
        """
        Sets the type of this Option.

        :param type: the type of this Option
        """
        self.type = type
    
    def set_value_separator(self, sep: str):
        """
        Sets the value separator. For example if the argument value was a Java property, the value separator would be '='.

        :param sep: The value separator.
        """
        self.valuesep = sep

    def to_string(self):
        """
        Dump state, suitable for debugging.

        :return: Stringified form of this object
        """
        buf = f"[ option: {self.option}"

        if self.long_option is not None:
            buf += f" {self.long_option}"

        buf += " "

        if self.has_args():
            buf += "[ARG...]"
        elif self.has_arg():
            buf += " [ARG]"

        buf += f" :: {self.description}"

        if self.type is not None:
            buf += f" :: {self.type}"

        buf += " ]"

        return buf
    
    def __str__(self):
        return self.to_string()
