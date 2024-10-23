from main.python.option import Option
from main.python.java_handler import java_handler, Types

@java_handler
class OptionBuilder:
    """
    OptionBuilder allows the user to create Options using descriptive methods that follows builder pattern.
    """

    long_option = None
    description = None
    arg_name = None
    required = False
    arg_count = Option.UNINITIALIZED
    type = Types.String
    optional_arg = False
    value_separator = '\0'
    
    @staticmethod
    def create(opt = None, no_func_arg = True) -> Option:
        """
        Creates an Option using the current settings.
        :param opt: the character representation of the Option
        :return: the Option instance
        :raises: ValueError if long_opt has not been set or opt is not a valid character. See Option.
        """
        if no_func_arg and opt is None:
            if OptionBuilder.long_option is None:
                OptionBuilder.reset()
                raise ValueError("must specify longopt")
            
            return OptionBuilder.create(None, False)
        
        option = None
        try:
            # create the option
            option = Option(opt, OptionBuilder.description)

            # set the option properties
            option.set_long_opt(OptionBuilder.long_option)
            option.set_required(OptionBuilder.required)
            option.set_optional_arg(OptionBuilder.optional_arg)
            option.set_args(OptionBuilder.arg_count)
            option.set_type(OptionBuilder.type)
            option.set_value_separator(OptionBuilder.value_separator)
            option.set_arg_name(OptionBuilder.arg_name)
        finally:
            # reset the OptionBuilder properties
            OptionBuilder.reset()

        # return the Option instance
        return option

    @staticmethod
    def has_arg(has_arg=None):
        """
        The next Option created will require an argument value if 'has_arg' is true.

        If 'has_arg' is None, the next Option will require an argument value.

        :param has_arg: if true then the Option has an argument value
        :return: the OptionBuilder instance
        """
        if has_arg is None:
            OptionBuilder.arg_count = 1
        else:
            OptionBuilder.arg_count = 1 if has_arg else Option.UNINITIALIZED

        return OptionBuilder

    
    @staticmethod
    def has_args(num=None):
        """
        Specifies the number of arguments the next Option created can have.
        If `num` is None, the next Option created can have unlimited argument values.
        
        :param num: Optional; The number of args that the option can have. 
                    If not provided, Option can have unlimited values. 
                    Default is None.
        :return: OptionBuilder instance with arg_count set according to provided `num`.
        """
        if num is None:
            OptionBuilder.arg_count = Option.UNLIMITED_VALUES
        else:
            OptionBuilder.arg_count = num

        return OptionBuilder

    
    @staticmethod
    def has_optional_arg():
        """
        The next Option can have an optional argument.
        
        :return: the OptionBuilder instance
        """
        OptionBuilder.arg_count = 1
        OptionBuilder.optional_arg = True

        return OptionBuilder
    
    @staticmethod
    def has_optional_args(num_args = None):
        """
        Specifies the number of optional arguments the next Option can have. 

        If num_args is not provided, the next Option created can have an unlimited number of optional arguments. 
        If num_args is provided, the next Option created can have up to num_args optional arguments.
        
        :param num_args: Optional; the maximum number of optional arguments the next Option created can have.
        :return: the OptionBuilder instance
        """
        if num_args is None:
            OptionBuilder.arg_count = Option.UNLIMITED_VALUES
            OptionBuilder.optional_arg = True
        else:
            OptionBuilder.arg_count = num_args
            OptionBuilder.optional_arg = True

        return OptionBuilder

        
    @staticmethod
    def is_required(required = None):
        """
        Specifies whether the next Option created will be required or not. 
        
        If required is not provided, the next Option will be required. 
        If required is provided, the next Option will be required if required is true.
        
        :param required: Optional; if true then the Option is required
        :return: the OptionBuilder instance
        """
        if required is None:
            OptionBuilder.required = True
        else:
            OptionBuilder.required = required

        return OptionBuilder


    @staticmethod
    def reset():
        """
        Resets the member variables to their default values.
        """
        OptionBuilder.description = None
        OptionBuilder.arg_name = None
        OptionBuilder.long_option = None
        OptionBuilder.type = Types.String
        OptionBuilder.required = False
        OptionBuilder.arg_count = Option.UNINITIALIZED
        OptionBuilder.optional_arg = False
        OptionBuilder.value_separator = '\0'

    @staticmethod
    def with_arg_name(name: str):
        """
        The next Option created will have the specified argument value name.
        
        :param name: the name for the argument value
        :return: the OptionBuilder instance
        """
        OptionBuilder.arg_name = name

        return OptionBuilder
    
    @staticmethod
    def with_description(new_description: str):
        """
        The next Option created will have the specified description
        
        :param new_description: a description of the Option's purpose
        :return: the OptionBuilder instance
        """
        OptionBuilder.description = new_description

        return OptionBuilder
    
    @staticmethod
    def with_long_opt(new_long_opt: str):
        """
        The next Option created will have the following long option value.
        
        :param new_long_opt: the long option value
        :return: the OptionBuilder instance
        """
        OptionBuilder.long_option = new_long_opt

        return OptionBuilder
    
    @staticmethod
    def with_type(new_type: type):
        """
        The next Option created will have a value that will be an instance of type.
        
        :param new_type: the type of the Options argument value
        :return: the OptionBuilder instance
        """
        OptionBuilder.type = new_type

        return OptionBuilder
    
    # 
    # The translation with Object argument has been omitted
    # as Python does not have the Object type
    #

    @staticmethod
    def with_value_separator(seperator=None):
        """
        Specifies the character to be used as a separator for argument values in the next Option created. 

        If no separator is provided, '=' will be used as the default separator.
        If a separator is provided, that will be used as the separator for argument values.

        :param seperator: Optional; the value separator to be used for the argument values.
        :return: the OptionBuilder instance
        """
        if seperator is None:
            OptionBuilder.value_separator = '='
        else:
            OptionBuilder.value_separator = seperator

        return OptionBuilder

