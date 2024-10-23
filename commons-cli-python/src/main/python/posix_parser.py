from main.python.ambiguous_option_exception import AmbiguousOptionException
from main.python.parser import Parser

class PosixParser(Parser):
    """
    Provides an implementation of the flatten method.
    Deprecated since 1.3, use the DefaultParser instead.
    """
    def __init__(self):
        # Holder for flattened tokens.
        self.tokens = []
        
        # Specifies if bursting should continue.
        self.eat_the_rest = False
        
        # Holder for the current option.
        self.current_option = None
        
        # The command line Options.
        self.options = None

    def burst_token(self, token, stop_at_non_option):
        """
        Breaks token into its constituent parts.
        """
        for i in range(1, len(token)):
            ch = token[i]
            
            if not self.options.has_option(ch):
                if stop_at_non_option:
                    self._process_non_option_token(token[i:], True)
                else:
                    self.tokens.append(token)
                break
                
            self.tokens.append("-" + ch)
            self.current_option = self.options.get_option(ch)

            if self.current_option.has_arg() and len(token) != i + 1:
                self.tokens.append(token[i + 1:])
                break

    def flatten(self, options, arguments, stop_at_non_option):
        """
        Implementation of Parser's abstract flatten method.
        """
        self._init()
        self.options = options

        args_iter = iter(arguments)

        # Process each command line token
        for token in args_iter:
            
            if token == "-" or token == "--":
                self.tokens.append(token)

            # Handle long option --foo or --foo=bar
            elif token.startswith("--"):
                pos = token.find('=')
                opt = token if pos == -1 else token[:pos]

                matching_opts = options.get_matching_options(opt)

                if not matching_opts:
                    self._process_non_option_token(token, stop_at_non_option)
                elif len(matching_opts) > 1:
                    raise AmbiguousOptionException(opt, matching_opts)
                else:
                    self.current_option = options.get_option(matching_opts[0])
                    self.tokens.append("--" + self.current_option.long_option)
                    if pos != -1:
                        self.tokens.append(token[pos + 1:])

            elif token.startswith("-"):
                if len(token) == 2 or options.has_option(token):
                    self._process_option_token(token, stop_at_non_option)
                elif options.get_matching_options(token):
                    matching_opts = options.get_matching_options(token)
                    if len(matching_opts) > 1:
                        raise AmbiguousOptionException(token, matching_opts)
                    opt = options.get_option(matching_opts[0])
                    self._process_option_token("-" + opt.long_option, stop_at_non_option)
                # Requires bursting
                else:
                    self.burst_token(token, stop_at_non_option)
            else:
                self._process_non_option_token(token, stop_at_non_option)

            self._gobble(args_iter)

        return self.tokens

    def _gobble(self, iter):
        """
        Adds the remaining tokens to the processed tokens list.
        """
        if self.eat_the_rest:
            self.tokens.extend(iter)

    def _init(self):
        """
        Resets the members to their original state i.e. remove all of tokens entries and set eatTheRest to False.
        """
        self.eat_the_rest = False
        self.tokens.clear()

    def _process_non_option_token(self, value, stop_at_non_option):
        """
        Adds the special token "--" and the current value to the processed tokens list. Then add all the
        remaining argument values to the processed tokens list.
        """
        if stop_at_non_option and (self.current_option is None or not self.current_option.has_arg()):
            self.eat_the_rest = True
            self.tokens.append("--")

        self.tokens.append(value)

    def _process_option_token(self, token, stop_at_non_option):
        """
        If an Option exists for token then add the token to the processed list.
        If an Option does not exist and stopAtNonOption is set then add the remaining tokens to the
        processed tokens list directly.
        """
        if stop_at_non_option and not self.options.has_option(token):
            self.eat_the_rest = True

        if self.options.has_option(token):
            self.current_option = self.options.get_option(token)

        self.tokens.append(token)
