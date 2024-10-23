import io
import os
import sys
from typing import List, Optional
from main.python.option import Option
from main.python.options import Options
from main.python.option_group import OptionGroup
from main.python.java_handler import java_handler

@java_handler
class HelpFormatter:
    DEFAULT_WIDTH = 74
    DEFAULT_LEFT_PAD = 1
    DEFAULT_DESC_PAD = 3
    DEFAULT_SYNTAX_PREFIX = "usage: "
    DEFAULT_OPT_PREFIX = "-"
    DEFAULT_LONG_OPT_PREFIX = "--"
    DEFAULT_LONG_OPT_SEPARATOR = " "
    DEFAULT_ARG_NAME = "arg"
    DEFAULT_NEW_LINE = os.linesep

    class OptionComparator:
        """
        This class mocks the interface for comparing Options.
        """
        def __init__(self):
            pass

        def compare(self, opt: Option) -> str:
            """
            Returns the casefolded key of the provided Option instance. 
            This method is used for sorting options in a case-insensitive manner.
            """
            return opt.get_key().casefold()

    def __init__(self):
        # Default number of characters per line
        self.width = HelpFormatter.DEFAULT_WIDTH
        
        # Default padding to the left of each line
        self.left_pad = HelpFormatter.DEFAULT_LEFT_PAD

        # Number of space characters to be prefixed to each description line
        self.desc_pad = HelpFormatter.DEFAULT_DESC_PAD
        
        # The string to display at the beginning of the usage statement
        self.syntax_prefix = HelpFormatter.DEFAULT_SYNTAX_PREFIX

        # Default prefix for short_opts
        self.opt_prefix = HelpFormatter.DEFAULT_OPT_PREFIX

        # Default prefix for long option
        self.long_opt_prefix = HelpFormatter.DEFAULT_LONG_OPT_PREFIX

        # Default separator displayed between a long Option and its value
        self.long_opt_separator = HelpFormatter.DEFAULT_LONG_OPT_SEPARATOR

        # The new line string
        self.new_line = HelpFormatter.DEFAULT_NEW_LINE
        
        # Comparator used to sort the options when they output in help text
        # Defaults to case-insensitive alphabetical sorting by option key
        self.option_comparator = HelpFormatter.OptionComparator()
        
        self.default_width = HelpFormatter.DEFAULT_WIDTH
        self.default_left_pad = HelpFormatter.DEFAULT_LEFT_PAD
        self.default_desc_pad = HelpFormatter.DEFAULT_DESC_PAD
        self.default_syntax_prefix = HelpFormatter.DEFAULT_SYNTAX_PREFIX
        self.default_new_line = os.linesep
        self.default_opt_prefix = HelpFormatter.DEFAULT_OPT_PREFIX
        self.default_long_opt_prefix = HelpFormatter.DEFAULT_LONG_OPT_PREFIX
        self.default_arg_name = HelpFormatter.DEFAULT_ARG_NAME
        self.long_opt_separator = HelpFormatter.DEFAULT_LONG_OPT_SEPARATOR

    def _append_option(self, buff: list, option: Option, required: bool) -> None:
        """
        Appends the usage clause for an Option to a list, which is used here as a replacement for Java's StringBuffer.

        Args:
            buff: The list to append to.
            option: The Option to append.
            required: Whether the Option is required or not.
        """
        if not required:
            buff.append("[")

        if option.get_opt():
            buff.append("-" + option.get_opt())
        else:
            buff.append("--" + option.get_long_opt())
        
        undefined_arg_name = option.get_arg_name() == None

        # If the Option has a value and a non-blank argname
        if option.has_arg() and (undefined_arg_name or len(option.get_arg_name().strip()) != 0):
            buff.append(self.long_opt_separator if not option.get_opt() else " ")
            buff.append("<" + (option.get_arg_name() if option.get_arg_name() else self.default_arg_name) + ">")

        # If the Option is not a required option
        if not required:
            buff.append("]")

    def _append_option_group(self, buff: list, group: OptionGroup) -> None:
        """
        Appends the usage clause for an OptionGroup to a list. The clause is wrapped in 
        square brackets if the group is required. The display of the options is handled by _append_option().

        Args:
            buff: The list to append to.
            group: The OptionGroup to append.
        """
        if not group.is_required():
            buff.append("[")

        opt_list = list(group.get_options())
        
        if (self.option_comparator):
            opt_list = sorted(opt_list, key=self.option_comparator.compare)

        for option in opt_list:
            self._append_option(buff, option, True)
            if option != opt_list[-1]:
                buff.append(" | ")

        if not group.is_required():
            buff.append("]")

    def create_padding(self, len: int) -> str:
        """
        Return a string of padding of specified length.

        Args:
            len: The length of the String of padding to create.

        Returns:
            The string of padding
        """
        return " " * len
    

    def find_wrap_pos(self, text: str, width: int, start_pos: int) -> int:
        """
        Finds the next text wrap position after 'startPos' for the text in 'text' with the column width 'width'.
        The wrap point is the last position before startPos+width having a whitespace character (space, \n, \r).
        If there is no whitespace character before startPos+width, it will return startPos+width.

        Args:
            text (str): The text being searched for the wrap position
            width (int): width of the wrapped text
            start_pos (int): position from which to start the lookup whitespace character

        Returns:
            int: Position on which the text must be wrapped or -1 if the wrap position is at the end of the text
        """

        # The line ends before the max wrap pos or a new line char found
        pos = text.find('\n', start_pos)
        if pos != -1 and pos <= width:
            return pos + 1

        # Check if a tab character is found before the max wrap position
        pos = text.find('\t', start_pos)
        if pos != -1 and pos <= width:
            return pos + 1

        # If the start position plus the width exceeds the length of the text, return -1
        if start_pos + width >= len(text):
            return -1

        # Look for the last whitespace character before startPos+width
        for pos in range(start_pos + width, start_pos - 1, -1):
            if text[pos] in (' ', '\n', '\r'):
                break

        # If no whitespace character was found, set the position to be startPos+width
        if pos <= start_pos:
            pos = start_pos + width

        # Return the position or -1 if the position is at the end of the text
        return -1 if pos == len(text) else pos

    def get_arg_name(self) -> str:
        """
        Gets the 'arg_name'.

        Returns:
            str: The 'arg_name'
        """
        return self.default_arg_name
    
    def get_desc_padding(self) -> int:
        """
        Gets the 'desc_padding'.

        Returns:
            int: The 'desc_padding'
        """
        return self.default_desc_pad

    def get_left_padding(self) -> int:
        """
        Gets the 'left_padding'.

        Returns:
            int: The 'left_padding'
        """
        return self.default_left_pad
    
    def get_long_opt_prefix(self) -> str:
        """
        Gets the 'long_opt_prefix'.

        Returns:
            str: The 'long_opt_prefix'
        """
        return self.default_long_opt_prefix
    
    def get_long_opt_separator(self) -> str:
        """
        Gets the separator displayed between a long option and its value.

        Returns:
            str: The separator
        """
        return self.long_opt_separator
    
    def get_new_line(self) -> str:
        """
        Gets the 'new_line'.

        Returns:
            str: The 'new_line'
        """
        return self.default_new_line
    
    def get_option_comparator(self):
        """
        Gets the comparator used to sort the options when they output in help text. Defaults to case-insensitive alphabetical sorting

        Returns:
            Comparator: The Comparator currently in use to sort the options
        """
        return self.option_comparator
    
    def get_opt_prefix(self) -> str:
        """
        Gets the 'opt_prefix'.

        Returns:
            str: The 'opt_prefix'
        """
        return self.default_opt_prefix
    
    def get_syntax_prefix(self) -> str:
        """
        Gets the 'syntax_prefix'.

        Returns:
            str: The 'syntax_prefix'
        """
        return self.default_syntax_prefix
    
    def get_width(self) -> int:
        """
        Gets the 'width'.

        Returns:
            int: The 'width'
        """
        return self.default_width
    
    def print_help(self, cmd_line_syntax: str, options: Options, pw: io.StringIO = sys.stdout, width: Optional[int] = None, 
               header: Optional[str] = None, left_pad: Optional[int] = None, desc_pad: Optional[int] = None, 
               footer: Optional[str] = None, auto_usage: bool = False) -> None:
        """
        Print the help for options with the specified command line syntax. This method prints help information
        to System.out if a custom writer is not specified.

        Args:
            cmd_line_syntax (str): The syntax for this application
            options (Options): The Options instance
            pw (io.StringIO, optional): The writer to which the help will be written. Defaults to None.
            width (int, optional): The number of characters to be displayed on each line. Defaults to None.
            header (str, optional): The banner to display at the beginning of the help. Defaults to None.
            left_pad (int, optional): The number of characters of padding to be prefixed to each line. Defaults to None.
            desc_pad (int, optional): The number of characters of padding to be prefixed to each description line. Defaults to None.
            footer (str, optional): The banner to display at the end of the help. Defaults to None.
            auto_usage (bool, optional): Whether to print an automatically generated usage statement. Defaults to False.

        Raises:
            ValueError: If the cmd_line_syntax is not provided

        Note:
            In case of insufficient room to print a line, an error will be raised during execution.
        """

        if not cmd_line_syntax:
            raise ValueError("cmd_line_syntax not provided")

        width = self.width if width is None else width
        left_pad = self.left_pad if left_pad is None else left_pad
        desc_pad = self.desc_pad if desc_pad is None else desc_pad

        # Print usage statement, generated automatically if auto_usage is True
        if auto_usage:
            self.print_usage(pw=pw, width=width, app=cmd_line_syntax, options=options)
        else:
            self.print_usage(pw=pw, width=width, cmd_line_syntax=cmd_line_syntax)

        # Print header, if provided
        if header and len(header) > 0:
            self.print_wrapped(pw=pw, width=width, text=header)

        # Print options with specified padding
        self.print_options(pw=pw, width=width, options=options, left_pad=left_pad, desc_pad=desc_pad)

        # Print footer, if provided
        if footer and len(footer) > 0:
            self.print_wrapped(pw=pw, width=width, text=footer)


    def print_options(self, pw: io.StringIO, width: int, options: Options, left_pad: int, desc_pad: int):
        """
        Print the help for the specified Options to the specified writer, using the specified width, left padding, and
        description padding.

        Args:
            pw (io.StringIO): The writer to write the help to
            width (int): The number of characters to display per line
            options (Options): The command line Options
            left_pad (int): The number of characters of padding to be prefixed to each line
            desc_pad (int): The number of characters of padding to be prefixed to each description line
        """

        sb = []

        # Render the options to the StringBuffer with specified padding
        self.render_options(sb, width, options, left_pad, desc_pad)
        
        # Print the rendered options
        pw.write(''.join(sb) + os.linesep)


    def print_usage(self, pw: io.StringIO, width: int, cmd_line_syntax: Optional[str] = None,
                    app: Optional[str] = None, options: Optional[Options] = None, 
                    _buff: List = None, _opt_list: List = None) -> Optional[str]:
        """
        Print the cmd_line_syntax or the usage statement for the specified application to the specified writer, using the specified width.

        Args:
            pw (io.StringIO): The writer to write the help to
            width (int): The number of characters per line for the usage statement.
            cmd_line_syntax (str, optional): The usage statement. Defaults to None.
            app (str, optional): The application name. Defaults to None.
            options (Options, optional): The command line Options. Defaults to None.
            buff (List, optional): [FOR GRAAL] The list or StringBuffer to append the usage statement to. Defaults to None.
        """

        if not _buff and (not app or not options):
            arg_pos = cmd_line_syntax.find(' ') + 1
            # Print wrapped cmdLineSyntax
            self.print_wrapped(pw=pw, width=width, next_line_tab_stop=len(self.syntax_prefix) + arg_pos, text=self.syntax_prefix + cmd_line_syntax)
        
        else:
            buff = _buff if _buff else [self.syntax_prefix + app + " "]
            # Set for processed option groups
            processed_groups = set()

            # Create a list for options and sort if comparator is set
            opt_list = _opt_list if _opt_list else list(options.get_options())
            
            # list already sorted from Java
            if(_opt_list):
                # extract python objects from java objects
                opt_list = [opt.getPythonObject() for opt in opt_list]

            # sort the list in Python
            elif(self.option_comparator):
                opt_list = sorted(opt_list, key=self.option_comparator.compare)

            for option in opt_list:
                # Check if the option is part of an OptionGroup
                group = options.get_option_group(option)
                # If the option is part of a group and the group has not already been processed
                if group and group not in processed_groups:
                    processed_groups.add(group)

                    # Add the usage clause
                    self._append_option_group(buff, group)
                
                # If the Option is not part of an OptionGroup
                elif not group:
                    self._append_option(buff, option, option.is_required())
                # If it's not the last option, append space
                if option != opt_list[-1]:
                    buff.append(" ")
            
            # if _buff is defined, return the buffer to the Java API
            if _buff: return buff
            else: 
                self.print_wrapped(pw, width, ''.join(buff), ''.join(buff).find(' ') + 1)


    def print_wrapped(self, pw: io.StringIO, width: int, text: str, next_line_tab_stop: int = 0):
        """
        Print the specified text to the specified writer.
        
        Args:
            pw (io.StringIO): The writer to write the help to
            width (int): The number of characters to display per line
            next_line_tab_stop (int, optional): The position on the next line for the first tab. Defaults to 0.
            text (str): The text to be written to the writer.
        """
        if text is not None:
            sb = []
            self._render_wrapped_text_block(sb, width, next_line_tab_stop, text)
            pw.write(''.join(sb))
            pw.write(os.linesep)

    
    def render_options(self, sb: List[str], width: int, options: Options, left_pad: int, desc_pad: int, _opt_list: List = None) -> List[str]:
        """
        Render the specified Options and return the rendered Options in a list.
        
        Args:
            sb (List[str]): The list to place the rendered Options into.
            width (int): The number of characters to display per line
            options (Options): The command line Options
            left_pad (int): the number of characters of padding to be prefixed to each line
            desc_pad (int): the number of characters of padding to be prefixed to each description line

        Returns:
            List[str]: the list with the rendered Options contents.
        """
        lpad = self.create_padding(left_pad)
        dpad = self.create_padding(desc_pad)

        # create list containing only <lpad>-a,--aaa where -a is opt and --aaa is long opt
        # also, look for the longest opt string, this list will be then used to sort options ascending
        max = 0
        prefix_list = []
        opt_list = _opt_list if _opt_list else options.help_options()
        
        if _opt_list:
            # extract python objects from java objects
            opt_list = [opt.getPythonObject() for opt in opt_list]
        elif(self.option_comparator):
            opt_list = sorted(opt_list, key=self.option_comparator.compare)

        for option in opt_list:
            opt_buf = []

            if not option.get_opt():
                opt_buf.append(lpad + "   " + self.long_opt_prefix + option.get_long_opt())
            else:
                opt_buf.append(lpad + self.opt_prefix + option.get_opt())
                if option.has_long_opt():
                    opt_buf.append(',' + self.long_opt_prefix + option.get_long_opt())

            if option.has_arg():
                arg_name = option.get_arg_name()
                if arg_name and arg_name.strip() == '':
                    opt_buf.append(' ')
                else:
                    opt_buf.append(self.long_opt_separator if option.has_long_opt() else " ")
                    opt_buf.append("<" + (arg_name if arg_name else self.default_arg_name) + ">")

            prefix_list.append(opt_buf)
            max = max if len(''.join(opt_buf)) <= max else len(''.join(opt_buf))

        x = 0

        for option in opt_list:
            opt_buf = prefix_list[x]
            x += 1

            if len(''.join(opt_buf)) < max:
                opt_buf.append(self.create_padding(max - len(''.join(opt_buf))))

            opt_buf.append(dpad)
            next_line_tab_stop = max + desc_pad

            if option.get_description() is not None:
                opt_buf.append(option.get_description())

            self.render_wrapped_text(sb, width, next_line_tab_stop, ''.join(opt_buf))

            if option != opt_list[-1]:
                sb.append(self.new_line)

        return sb
    
    def render_wrapped_text(self, sb: List[str], width: int, next_line_tab_stop: int, text: str) -> None:
        """
        Render the specified text and append the rendered lines to a list.
        
        Args:
            sb (List[str]): The list to append the rendered lines to.
            width (int): The number of characters to display per line.
            nextLineTabStop (int): The position on the next line for the first tab.
            text (str): The text to be rendered.

        Returns:
            None
        """
        pos = self.find_wrap_pos(text, width, 0)

        if pos == -1:
            sb.append(self.rtrim(text))
            return sb

        sb.append(self.rtrim(text[:pos]))
        sb.append(self.new_line)

        if next_line_tab_stop >= width:
            # Prevents an infinite loop
            next_line_tab_stop = 1

        # The following lines must be padded with 'next_line_tab_stop' number of space characters
        padding = self.create_padding(next_line_tab_stop)

        while True:
            text = padding + text[pos:].strip()
            pos = self.find_wrap_pos(text, width, 0)

            if pos == -1:
                sb.append(text)
                return sb

            if len(text) > width and pos == next_line_tab_stop - 1:
                pos = width

            sb.append(self.rtrim(text[:pos]))
            sb.append(self.new_line)


    def _render_wrapped_text_block(self, sb: List[str], width: int, next_line_tab_stop: int, text: str) -> List[str]:
        """
        Render the specified text with a maximum width. This method differs from `render_wrapped_text` 
        by not removing leading spaces after a new line.
        
        Args:
            sb (List[str]): The list to append the rendered lines to.
            width (int): The number of characters to display per line.
            nextLineTabStop (int): The position on the next line for the first tab.
            text (str): The text to be rendered.

        Returns:
            List[str]: The list with the rendered lines of text.
        """
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if i != 0:
                sb.append(self.new_line)
            self.render_wrapped_text(sb, width, next_line_tab_stop, line)
        return sb



    def rtrim(self, s: str) -> str:
        """
        Remove the trailing whitespace from the specified string.
        
        Args:
            s (str): The string to remove the trailing padding from.

        Returns:
            str: The string without trailing padding.
        """
        if not s:
            return s
        else:
            return s.rstrip()

    def set_arg_name(self, name: str) -> None:
        """
        Sets the 'arg_name'.

        Args:
            name (str): The new value of 'arg_name'
        """
        self.default_arg_name = name

    def set_desc_padding(self, padding: int) -> None:
        """
        Sets the 'desc_padding'.
        
        Args:
            padding (int): The new value of 'desc_padding'
        """
        self.default_desc_pad = padding

    def set_left_padding(self, padding: int) -> None:
        """
        Sets the 'left_padding'.

        Args:
            padding (int): The new value of 'left_padding'
        """
        self.default_left_pad = padding

    def set_long_opt_prefix(self, prefix: str) -> None:
        """
        Sets the 'long_opt_prefix'.

        Args:
            prefix (str): The new value of 'long_opt_prefix'
        """
        self.default_long_opt_prefix = prefix

    def set_long_opt_separator(self, long_opt_separator: str) -> None:
        """
        Set the separator displayed between a long option and its value. Ensure that the separator is
        supported by the parser used, typicall ' ' or '='.

        Args:
            long_opt_separator (str): the separator, typically ' ' or '='
        """
        self.long_opt_separator = long_opt_separator
    
    def set_new_line(self, new_line: str) -> None:
        """
        Sets the 'new_line'.

        Args:
            new_line (str): The new value of 'new_line'
        """
        self.default_new_line = new_line

    def set_option_comparator(self, comparator):
        """
        Set the comparator used to sort the options when they output in help text. Passing in a null comparator will keep the
        options in the order they were declared.

        Args:
            comparator (Comparator): the Comparator to use for sorting the options
        """
        self.option_comparator = comparator

    def set_opt_prefix(self, prefix: str) -> None:
        """
        Sets the 'opt_prefix'.

        Args:
            prefix (str): The new value of 'opt_prefix'
        """
        self.default_opt_prefix = prefix

    def set_syntax_prefix(self, prefix: str) -> None:
        """
        Sets the 'syntax_prefix'.

        Args:
            prefix (str): The new value of 'syntax_prefix'
        """
        self.default_syntax_prefix = prefix

    def set_width(self, width: int) -> None:
        """
        Sets the 'width'.

        Args:
            width (int): The new value of 'width'
        """
        self.default_width = width
