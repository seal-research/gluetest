from main.python.java_handler import java_handler

@java_handler
class Util:
    """
    Contains useful helper methods for classes within this package.
    """

    @staticmethod
    def strip_leading_and_trailing_quotes(s):
        """
        Remove the leading and trailing quotes from s. E.g. if s is '"one two"', then 'one two' is returned.

        :param s: The string from which the leading and trailing quotes should be removed.
        
        :return: The string without the leading and trailing quotes.
        """
        LENGTH = len(s)
        if LENGTH > 1 and s.startswith('"') and s.endswith('"') and s[1:LENGTH - 1].find('"') == -1:
            s = s[1:LENGTH - 1]
        return s

    @staticmethod
    def strip_leading_hyphens(s):
        """
        Remove the hyphens from the beginning of s and return the new string.
        
        :param s: The string from which the hyphens should be removed.
        
        :return: The new string.
        """
        if s is None:
            return None
        if s.startswith("--"):
            return s[2:]
        if s.startswith("-"):
            return s[1:]
        return s
