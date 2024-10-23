from main.python.parse_exception import ParseException 
class UnrecognizedOptionException(ParseException):
    def __init__(self, message, option=None):
        super().__init__(message)
        self.option = option

    def get_option(self):
        return self.option
