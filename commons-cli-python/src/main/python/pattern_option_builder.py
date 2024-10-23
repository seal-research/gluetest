import io
import urllib.parse
from main.python.options import Options
from main.python.option import Option
from main.python.java_handler import Types

class PatternOptionBuilder:
    """
    Allows Options to be created from a single String. The pattern contains various single character flags and via an
    optional punctuation character, their expected type.
    """

    # String class
    STRING_VALUE = Types.String

    # Object class
    OBJECT_VALUE = Types.Object

    # Number class
    NUMBER_VALUE = Types.Number

    # Date class
    DATE_VALUE = Types.Date

    # Class class
    CLASS_VALUE = Types.Class

    # File Input Stream class
    EXISTING_FILE_VALUE = Types.FileInputStream

    # File class
    FILE_VALUE = Types.File

    # File array class
    FILES_VALUE = Types.Files

    # URL class
    URL_VALUE = Types.URL

    @staticmethod
    def get_value_class(ch: str):
        """
        Retrieve the class that ch represents.

        :param ch: the specified character
        :return: The class that ch represents
        """
        if ch == '@':
            return PatternOptionBuilder.OBJECT_VALUE
        elif ch == ':':
            return PatternOptionBuilder.STRING_VALUE
        elif ch == '%':
            return PatternOptionBuilder.NUMBER_VALUE
        elif ch == '+':
            return PatternOptionBuilder.CLASS_VALUE
        elif ch == '#':
            return PatternOptionBuilder.DATE_VALUE
        elif ch == '<':
            return PatternOptionBuilder.EXISTING_FILE_VALUE
        elif ch == '>':
            return PatternOptionBuilder.FILE_VALUE
        elif ch == '*':
            return PatternOptionBuilder.FILES_VALUE
        elif ch == '/':
            return PatternOptionBuilder.URL_VALUE
        else:
            return None
    
    @staticmethod
    def is_value_code(ch: str):
        """
        Returns whether ch is a value code, i.e. whether it represents a class in a pattern.

        :param ch: the specified character
        :return: true if ch is a value code, otherwise false.
        """
        return len(ch) == 1 and ch in "@:%+#<>*/!"
    
    @staticmethod
    def parse_pattern(pattern: str):
        """
        Returns the Options instance represented by pattern.
        
        :param pattern: the pattern string
        :return: The Options instance
        """
        opt = ' '
        required = False
        type = None

        options = Options()

        for i in range(len(pattern)):
            ch = pattern[i]

            # a value code comes after an option and specifies
            # details about it
            if not PatternOptionBuilder.is_value_code(ch):
                if opt != ' ':
                    option = Option.builder(str(opt)).has_arg(type != None).required(required).type(type).build()

                    # we have a previous one to deal with
                    options.add_option(option)
                    required = False
                    type = None
                    opt = ' '

                opt = ch
            elif ch == '!':
                required = True
            else:
                type = PatternOptionBuilder.get_value_class(ch)

        if opt != ' ':
            option = Option.builder(str(opt)).has_arg(type != None).required(required).type(type).build()

            # we have a final one to deal with
            options.add_option(option)

        return options
