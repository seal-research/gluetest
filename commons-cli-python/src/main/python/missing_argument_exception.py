#!/usr/bin/env python
from main.python.parse_exception import ParseException    #  The option requiring additional arguments 
from main.python.java_handler import java_handler

@java_handler
class MissingArgumentException(ParseException):

    def __init__(self, option):
        if type(option) == str: # option is a string message
            super().__init__(option)
        else:
            # option is an Option object (foreign/native)
            self.__init__("Missing argument for option: " + option.get_key())
            self.option = option

    def get_option(self):
        return self.option
