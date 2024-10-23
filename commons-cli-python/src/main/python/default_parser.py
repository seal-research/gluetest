from main.python.parser import Parser
from main.python.util import Util
from main.python.options import Options
from main.python.option import Option
from main.python.missing_argument_exception import MissingArgumentException
from main.python.missing_option_exception import MissingOptionException
from main.python.ambiguous_option_exception import AmbiguousOptionException
from main.python.unrecognized_option_exception import UnrecognizedOptionException
from main.python.command_line import CommandLine
from main.python.java_handler import java_handler


@java_handler
class DefaultParser(Parser):
    def __init__(self, *args):
        if(len(args)==0):
            self.allow_partial_matching = True
            self.strip_leading_and_trailing_quotes = None
        elif(len(args)==1):

        # Creates a new DefaultParser instance with the specified partial matching and quote stripping policy.
        #
        # @param allowPartialMatching if partial matching of long options shall be enabled
        # @param stripLeadingAndTrailingQuotes if balanced outer double quoutes should be stripped
            allow_partial_matching = args[0]
            
            self.allow_partial_matching = allow_partial_matching
            self.strip_leading_and_trailing_quotes = None
        elif(len(args)==2):
            allow_partial_matching, strip_leading_and_trailing_quotes = args

            self.allow_partial_matching = allow_partial_matching
            self.strip_leading_and_trailing_quotes = strip_leading_and_trailing_quotes
     # A nested builder class to create {@code DefaultParser} instances
     # using descriptive methods.
     #
     # Example usage:
     # <pre>
     # DefaultParser parser = Option.builder()
     #     .setAllowPartialMatching(false)
     #     .setStripLeadingAndTrailingQuotes(false)
     #     .build();
     # </pre>
     #
     # @since 1.5.0

    @java_handler
    class Builder:
        def __init__(self):
            self.allow_partial_matching = True
            self.strip_leading_and_trailing_quotes = False

        def build(self):
            return DefaultParser(self.allow_partial_matching, self.strip_leading_and_trailing_quotes)

        def set_allow_partial_matching(self, set_allow_partial_matching):
            self.set_allow_partial_matching = set_allow_partial_matching
            return self

        def set_strip_leading_and_trailing_quotes(self, set_strip_leading_and_trailing_quotes):
            self.strip_leading_and_trailing_quotes = set_strip_leading_and_trailing_quotes
            return self

    def builder():
        return DefaultParser.Builder()

# Throws a {@link MissingArgumentException} if the required number of arguments are not present.

    def check_required_args(self):
        if self.current_option and self.current_option.requires_arg():
            raise MissingArgumentException(self.current_option)

 # Throws a {@link MissingOptionException} if all of the required options are not present.
 #
 # @throws MissingOptionException if any of the required Options are not present.

    def check_required_options(self):
        if self.expected_opts:
            raise MissingOptionException(self.expected_opts)



 # Searches for a prefix that is the long name of an option (-Xmx512m)
 #
 # @param token

    def get_long_prefix(self, token):
        t = Util.strip_leading_hyphens(token)
        opt = None
        for i in range(len(t) - 2, 1, -1):
            prefix = t[:i]
            if self.options.has_long_option(prefix):
                opt = prefix
                break
        return opt


 # Gets a list of matching option strings for the given token, depending on the selected partial matching policy.
 #
 # @param token the token (may contain leading dashes)
 # @return the list of matching option strings or an empty list if no matching option could be found

    def get_matching_long_options(self, token):
        if self.allow_partial_matching:
            return self.options.get_matching_options(token)
        matches = []
        if self.options.has_long_option(token):
            option = self.options.get_option(token)
            matches.append(option.get_long_opt())
        return matches

 # Breaks {@code token} into its constituent parts using the following algorithm.
 #
 # <ul>
 # <li>ignore the first character ("<b>-</b>")</li>
 # <li>for each remaining character check if an {@link Option} exists with that id.</li>
 # <li>if an {@link Option} does exist then add that character prepended with "<b>-</b>" to the list of processed
 # tokens.</li>
 # <li>if the {@link Option} can have an argument value and there are remaining characters in the token then add the
 # remaining characters as a token to the list of processed tokens.</li>
 # <li>if an {@link Option} does <b>NOT</b> exist <b>AND</b> {@code stopAtNonOption} <b>IS</b> set then add the
 # special token "<b>--</b>" followed by the remaining characters and also the remaining tokens directly to the
 # processed tokens list.</li>
 # <li>if an {@link Option} does <b>NOT</b> exist <b>AND</b> {@code stopAtNonOption} <b>IS NOT</b> set then add
 # that character prepended with "<b>-</b>".</li>
 # </ul>
 #
 # @param token The current token to be <b>burst</b> at the first non-Option encountered.
 # @throws ParseException if there are any problems encountered while parsing the command line token.

    def handle_concatenated_options(self, token):
        for i in range(1, len(token)):
            ch = token[i]

            if not self.options.has_option(ch):
                self.handle_unknown_token(token[i:] if self.stop_at_non_option and i > 1 else token)
                break
            self.handle_option(self.options.get_option(ch))

            if self.current_option is not None and len(token) != i + 1:
                # add the trail as an argument of the option
                self.current_option.add_value_for_processing(self.strip_leading_and_trailing_quotes_default_off(token[i + 1:]))
                break

     # Handles the following tokens:
     #
     # --L --L=V --L V --l
     #
     # @param token the command line token to handle

    def handle_long_option(self, token: str):
        if '=' not in token:
            self.handle_long_option_without_equal(token)
        else:
            self.handle_long_option_with_equal(token)

     # Handles the following tokens:
     #
     # --L=V -L=V --l=V -l=V
     #
     # @param token the command line token to handle

    def handle_long_option_with_equal(self, token: str):
        pos = token.find('=')
        value = token[pos + 1:]
        opt = token[:pos]

        matching_opts = self.get_matching_long_options(opt)
        if len(matching_opts) == 0:
            self.handle_unknown_token(self.current_token)
        elif len(matching_opts) > 1 and not self.options.has_long_option(opt):
            raise AmbiguousOptionException(opt, matching_opts)
        else:
            key = opt if self.options.has_long_option(opt) else matching_opts[0]
            option = self.options.get_option(key)

            if option.accepts_arg():
                self.handle_option(option)
                self.current_option.add_value_for_processing(self.strip_leading_and_trailing_quotes_default_off(value))
                self.current_option = None
            else:
                self.handle_unknown_token(self.current_token)

     # Handles the following tokens:
     #
     # --L -L --l -l
     #
     # @param token the command line token to handle

    def handle_long_option_without_equal(self,token):
        matching_opts = self.get_matching_long_options(token)
        if len(matching_opts) == 0:
            self.handle_unknown_token(self.current_token)
        elif len(matching_opts) > 1 and not self.options.has_long_option(token):
            raise AmbiguousOptionException(token, matching_opts)
        else:
            key = token if self.options.has_long_option(token) else matching_opts[0]
            self.handle_option(self.options.get_option(key))

    def handle_option(self,option):
        self.check_required_args()

        option = option.clone()

        self.update_required_options(option)

        self.cmd.add_option(option)

        if option.has_arg():
            self.current_option = option
        else:
            self.current_option = None

     # Sets the values of Options using the values in {@code properties}.
     #
     # @param properties The value properties to be processed.

    def handle_properties(self,properties):
        if properties is None:
            return

        for option in properties.keys():

            opt = self.options.get_option(option)
            if not opt:
                raise UnrecognizedOptionException("Default option wasn't defined", option)

            group = self.options.get_option_group(opt)
            selected = group and group.get_selected()

            if not self.cmd.has_option(option) and not selected:
                value = properties[option]

                if opt.has_arg():
                    if not opt.get_values() or len(opt.get_values()) == 0:
                        opt.add_value_for_processing(self.strip_leading_and_trailing_quotes_default_off(value))
                elif not (value.lower() in ["yes", "true", "1"]):
                    continue

                self.handle_option(opt)
                self.current_option = None

     # Handles the following tokens:
     #
     # -S -SV -S V -S=V -S1S2 -S1S2 V -SV1=V2
     #
     # -L -LV -L V -L=V -l
     #
     # @param token the command line token to handle

    def handle_short_and_long_option(self, token):
        t = token.lstrip('-')
        pos = t.find('=')

        if len(t) == 1:
            # -S
            if self.options.has_short_option(t):
                self.handle_option(self.options.get_option(t))
            else:
                self.handle_unknown_token(token)
        elif pos == -1:
            # no equal sign found (-xxx)
            if self.options.has_short_option(t):
                self.handle_option(self.options.get_option(t))
            elif self.get_matching_long_options(t):
                # -L or -l
                self.handle_long_option_without_equal(token)
            else:
                # look for a long prefix (-Xmx512m)
                opt = self.get_long_prefix(t)

                if opt and self.options.get_option(opt).accepts_arg():
                    self.handle_option(self.options.get_option(opt))
                    self.current_option.add_value_for_processing(self.strip_leading_and_trailing_quotes_default_off(t[len(opt):]))
                    self.current_option = None
                elif self.is_java_property(t):
                    # -SV1 (-Dflag)
                    self.handle_option(self.options.get_option(t[:1]))
                    self.current_option.add_value_for_processing(self.strip_leading_and_trailing_quotes_default_off(t[1:]))
                    self.current_option = None
                else:
                    # -S1S2S3 or -S1S2V
                    self.handle_concatenated_options(token)
        else:
            # equal sign found (-xxx=yyy)
            opt = t[:pos]
            value = t[pos + 1:]

            if len(opt) == 1:
                # -S=V
                option = self.options.get_option(opt)
                if option and option.accepts_arg():
                    self.handle_option(option)
                    self.current_option.add_value_for_processing(value)
                    self.current_option = None
                else:
                    self.handle_unknown_token(token)
            elif self.is_java_property(opt):
                # -SV1=V2 (-Dkey=value)
                self.handle_option(self.options.get_option(opt[:1]))
                self.current_option.add_value_for_processing(opt[1:])
                self.current_option.add_value_for_processing(value)
                self.current_option = None
            else:
                # -L=V or -l=V
                self.handle_long_option_with_equal(token)

     # Handles any command line token.
     #
     # @param token the command line token to handle
     # @throws ParseException

    def handle_token(self,token):
        self.current_token = token

        if self.skip_parsing:
            self.cmd.add_arg(token)
        elif token == "--":
            self.skip_parsing = True
        elif self.current_option is not None and self.current_option.accepts_arg() and self.is_argument(token):
            self.current_option.add_value_for_processing(self.strip_leading_and_trailing_quotes_default_on(token))
        elif token.startswith("--"):
            self.handle_long_option(token)
        elif token.startswith("-") and token != "-":
            self.handle_short_and_long_option(token)
        else:
            self.handle_unknown_token(token)

        if self.current_option is not None and not self.current_option.accepts_arg():
            self.current_option = None

     # Handles an unknown token. If the token starts with a dash an UnrecognizedOptionException is thrown. Otherwise the
     # token is added to the arguments of the command line. If the stopAtNonOption flag is set, this stops the parsing and
     # the remaining tokens are added as-is in the arguments of the command line.
     #
     # @param token the command line token to handle

    def handle_unknown_token(self,token):
        if token.startswith("-") and len(token) > 1 and not self.stop_at_non_option:
            raise UnrecognizedOptionException("Unrecognized option: " + token, token)

        self.cmd.add_arg(token)
        if self.stop_at_non_option:
            self.skip_parsing = True

     # Tests if the token is a valid argument.
     #
     # @param token

    def is_argument(self,token):
        return not self.is_option(token) or self.is_negative_number(token)

     # Tests if the specified token is a Java-like property (-Dkey=value).

    def is_java_property(self,token):
        opt = token[0]
        option = self.options.get_option(opt)

        return option and (option.get_args() >= 2 or option.get_args() == Option.UNLIMITED_VALUES)

     # Tests if the token looks like a long option.
     #
     # @param token

    def is_long_option(self,token):
        if token is None or not token.startswith("-") or len(token) == 1:
            return False

        pos = token.index("=") if "=" in token else -1
        t = token if pos == -1 else token[:pos]

        if len(self.get_matching_long_options(t)) > 0:
            return True
        if self.get_long_prefix(token) and not token.startswith("--"):
            return True

        return False


     # Tests if the token is a negative number.
     #
     # @param token

    def is_negative_number(self,token):
        try:
            float(token)
            return True
        except ValueError:
            return False

     # Tests if the token looks like an option.
     #
     # @param token

    def is_option(self,token):
        return self.is_long_option(token) or self.is_short_option(token)

     # Tests if the token looks like a short option.
     #
     # @param token

    def is_short_option(self,token):
        if token is None or not token.startswith("-") or len(token) == 1:
            return False

        pos = token.index("=") if "=" in token else -1
        opt_name = token[1:pos] if pos != -1 else token[1:]

        if self.options.has_short_option(opt_name):
            return True

        return len(opt_name) > 0 and self.options.has_short_option(opt_name[0])

    def parse(self, *args):
        if len(args) == 2:
            options, arguments = args
            return self.parse(options, arguments, None)
        elif len(args) == 3:
            if isinstance(args[2], bool):
                options, arguments, stop_at_non_option = args
                return self.parse(options, arguments, None, stop_at_non_option)
            else:
                options, arguments, properties = args
                return self.parse(options, arguments, properties, False)
        elif len(args) == 4:
            options, arguments, properties, stop_at_non_option = args
            self.options = options
            self.stop_at_non_option = stop_at_non_option
            self.skip_parsing = False
            self.current_option = None
            self.expected_opts = list(options.get_required_options())

            for group in options.get_option_groups():
                group.set_selected(None)

            self.cmd = CommandLine()

            if arguments is not None:
                for argument in arguments:
                    self.handle_token(argument)

            self.check_required_args()
            self.handle_properties(properties)
            self.check_required_options()

            return self.cmd

     # Strips balanced leading and trailing quotes if the stripLeadingAndTrailingQuotes is set
     # If stripLeadingAndTrailingQuotes is null, then do not strip
     #
     # @param token a string
     # @return token with the quotes stripped (if set)

    def strip_leading_and_trailing_quotes_default_off(self, token):
        if self.strip_leading_and_trailing_quotes:
            return Util.strip_leading_and_trailing_quotes(token)
        return token

     # Strips balanced leading and trailing quotes if the stripLeadingAndTrailingQuotes is set
     # If stripLeadingAndTrailingQuotes is null, then do not strip
     #
     # @param token a string
     # @return token with the quotes stripped (if set)

    def strip_leading_and_trailing_quotes_default_on(self,token):
        if self.strip_leading_and_trailing_quotes is None or self.strip_leading_and_trailing_quotes:
            return Util.strip_leading_and_trailing_quotes(token)
        return token

     # Removes the option or its group from the list of expected elements.
     #
     # @param option

    def update_required_options(self, option: Option):
        if option.is_required():
            self.expected_opts.remove(option.get_key())

        if self.options.get_option_group(option):
            group = self.options.get_option_group(option)

            if group.is_required():
                self.expected_opts.remove(group)

            group.set_selected(option)
