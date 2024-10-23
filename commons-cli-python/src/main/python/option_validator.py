from main.python.java_handler import java_handler

@java_handler
class OptionValidator:

    @staticmethod
    def is_valid_char(c):
        """
        Returns whether c can be part of a python identifier as other than the first character.
        """
        return c.isalnum() or c == '_'

    @staticmethod
    def is_valid_opt(c):
        """
        Returns whether the specified character is a valid option.

        :param c: the option to validate
        :return: true if c is a letter, '?' or '@', false otherwise
        """
        return OptionValidator.is_valid_char(c) or c == '?' or c == '@'

    @staticmethod
    def validate(option: str = None):
        """
        Validates whether opt is a valid Option shortOpt. The rules that specify if the {@code opt}
        is valid are:

        - a single character opt that is either ' ' (special case), '?', '@' or a letter
        - a multi character opt that only contains letters.

        In case opt is None, no further validation is performed.

        :param option: the option string to validate, may be None
        :raises ValueError: if the Option is not valid
        """
        # if opt is NULL do not check further
        if option is None:
            return None

        # handle the single character opt
        if len(option) == 1:
            ch = option[0]
            if not OptionValidator.is_valid_opt(ch):
                raise ValueError(f"Illegal option name '{ch}'")
        else:
            # handle the multi character opt
            for ch in option:
                #
                # One-to-one translation would be:
                # if not OptionValidator.is_valid_char(ch): 
                #
                # But, the actual Java code is not correct because it allows  
                # not just letters but also '?' and '@' 
                # I am assuming that is_valid_char is the correct method to use
                #
                if not OptionValidator.is_valid_char(ch):
                    raise ValueError(f"The option {option} contains an illegal character : '{option}'")
        
        return option
