class ParseException(Exception):
    def __init__(self, message):
        super().__init__(message)
    
    def get_message(self):
        return str(self)
