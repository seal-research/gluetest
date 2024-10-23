from main.python.parser import Parser
from main.python.util import Util
from main.python.java_handler import java_handler

@java_handler
class GnuParser(Parser):
    def flatten(self, options, arguments, stop_at_non_option):
        tokens = []
        eat_the_rest = False
        i = 0
        while i < len(arguments):
            arg = arguments[i]
            if arg == "--":
                eat_the_rest = True
                tokens.append("--")
            elif arg == "-":
                tokens.append("-")
            elif arg.startswith("-"):
                opt = Util.strip_leading_hyphens(arg)

                # if opt in options:
                if options.has_option(opt):
                    tokens.append(arg)
                elif '=' in opt and options.has_option(opt[:opt.index('=')]):
                    # the format is --foo=value or -foo=value
                    tokens.append(arg[:arg.index('=')])  # --foo
                    tokens.append(arg[arg.index('=') + 1:])  # value
                elif options.has_option(arg[:2]):
                    # the format is a special properties option (-Dproperty=value)
                    tokens.append(arg[:2])  # -D
                    tokens.append(arg[2:])  # property=value
                else:
                    eat_the_rest = stop_at_non_option
                    tokens.append(arg)
            else:
                tokens.append(arg)
            if eat_the_rest:
                i += 1
                while i < len(arguments):
                    tokens.append(arguments[i])
                    i += 1
            i += 1
        return tokens
