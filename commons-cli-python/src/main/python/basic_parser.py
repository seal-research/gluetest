from main.python.parser import Parser
from main.python.java_handler import java_handler

@java_handler
class BasicParser(Parser):
    def flatten(self, options, arguments, stop_at_non_option):
        return arguments
