from main.python.token import Token
from main.python.constants import Constants
from main.python.csv_format import CSVFormat
from main.python.extended_buffered_reader import ExtendedBufferedReader
from main.python.closeable import Closeable
from main.python.java_handler import java_handler


@java_handler
class Lexer(Closeable):
    DISABLED = '\ufffe'

    def __init__(self, formatter: CSVFormat, reader: ExtendedBufferedReader):
        self.reader = reader
        self.delimiter = formatter.get_delimiter()
        self.escape = self.map_null_to_disabled(
            formatter.get_escape_character()
        )
        self.quote_char = self.map_null_to_disabled(
            formatter.get_quote_character()
        )
        self.comment_start = self.map_null_to_disabled(
            formatter.get_comment_marker()
        )
        self.ignore_surrounding_spaces = \
            formatter.get_ignore_surrounding_spaces()
        self.ignore_empty_lines = formatter.get_ignore_empty_lines()
        self.first_eol = None

    def get_first_eol(self):
        return self.first_eol

    def next_token(self, token: Token):
        last_char = self.reader.get_last_char()
        c = self.reader.read()
        eol = self.read_end_of_line(c)

        if self.ignore_empty_lines:
            while eol and self.is_start_of_line(last_char):
                last_char = c
                c = self.reader.read()
                eol = self.read_end_of_line(c)

                if self.is_end_of_file(c):
                    token.set_type(Token.Type.EOF)
                    return token

        if (
            self.is_end_of_file(last_char) or
            (not self.is_delimiter(last_char)
                and self.is_end_of_file(c))
        ):
            token.set_type(Token.Type.EOF)
            return token

        if self.is_start_of_line(last_char) and self.is_comment_start(c):
            line = self.reader.read_line()
            if line is None:
                token.set_type(Token.Type.EOF)
                return token
            comment = line.strip()
            token.append(comment)
            token.set_type(Token.Type.COMMENT)
            return token

        while token.get_type() == Token.Type.INVALID:
            if self.ignore_surrounding_spaces:
                while self.is_whitespace(c) and not eol:
                    c = self.reader.read()
                    eol = self.read_end_of_line(c)

            if self.is_delimiter(c):
                token.set_type(Token.Type.TOKEN)
            elif eol:
                token.set_type(Token.Type.EORECORD)
            elif self.is_quote_char(c):
                self.parse_encapsulated_token(token)
            elif self.is_end_of_file(c):
                token.set_type(Token.Type.EOF)
                token.set_ready(True)
            else:
                self.parse_simple_token(token, c)

        return token

    def parse_simple_token(self, token: Token, ch: int):
        while True:
            if self.read_end_of_line(ch):
                token.set_type(Token.Type.EORECORD)
                break
            elif self.is_end_of_file(ch):
                token.set_type(Token.Type.EOF)
                token.is_ready = True
                break
            elif self.is_delimiter(ch):
                token.set_type(Token.Type.TOKEN)
                break
            elif self.is_escape(ch):
                unescaped = self.read_escape()
                if unescaped == Constants.END_OF_STREAM:
                    token.append(ch)
                    token.append(self.reader.get_last_char())
                else:
                    token.content += unescaped
                ch = self.reader.read()
            else:
                token.append(ch)
                ch = self.reader.read()

        if self.ignore_surrounding_spaces:
            self.trim_trailing_spaces(token)

        return token

    def parse_encapsulated_token(self, token: Token):
        start_line_number = self.get_current_line_number()
        c = self.reader.read()
        while True:
            if self.is_escape(c):
                unescaped = self.read_escape()
                if unescaped == Constants.END_OF_STREAM:
                    token.append(c)
                    token.append(self.reader.get_last_char())
                else:
                    token.content += unescaped
            elif self.is_quote_char(c):
                if self.is_quote_char(self.reader.look_ahead()):
                    c = self.reader.read()
                    token.append(c)
                else:
                    while True:
                        c = self.reader.read()
                        if self.is_delimiter(c):
                            token.set_type(Token.Type.TOKEN)
                            return token
                        elif self.is_end_of_file(c):
                            token.set_type(Token.Type.EOF)
                            token.is_ready = True
                            return token
                        elif self.read_end_of_line(c):
                            token.set_type(Token.Type.EORECORD)
                            return token
                        elif not self.is_whitespace(c):
                            line_number = self.get_current_line_number()
                            error_msg = (
                                f"(line {line_number}) invalid char between "
                                f"encapsulated token and delimiter"
                            )
                            raise IOError(error_msg)
            elif self.is_end_of_file(c):
                error_msg = (
                    f"(startline {start_line_number}) EOF reached "
                    f"before encapsulated token finished"
                )
                raise IOError(error_msg)
            else:
                token.append(c)

            c = self.reader.read()

    def map_null_to_disabled(self, char: str):
        return self.DISABLED if char is None else char

    def get_current_line_number(self):
        return self.reader.get_current_line_number()

    def get_character_position(self):
        return self.reader.get_position()

    def read_escape(self):
        ch = self.reader.read()
        if ch == 'r':
            return Constants.CR
        if ch == 'n':
            return Constants.LF
        if ch == 't':
            return Constants.TAB
        if ch == 'b':
            return Constants.BACKSPACE
        if ch == 'f':
            return Constants.FF
        if ch in [Constants.CR,
                  Constants.LF,
                  Constants.FF,
                  Constants.TAB,
                  Constants.BACKSPACE]:
            return ch
        if ch == Constants.END_OF_STREAM:
            raise IOError("EOF whilst processing escape sequence")
        if self.is_meta_char(ch):
            return ch
        return Constants.END_OF_STREAM

    def trim_trailing_spaces(self, token: Token):
        buffer = token.get_content()
        length = len(buffer)
        while length > 0 and self._is_whitespace(buffer[length - 1]):
            length -= 1
        if length != len(buffer):
            buffer = buffer[:length]
        token.set_content(buffer)

    def read_end_of_line(self, ch: int):
        if ch == Constants.CR and self.reader.look_ahead() == Constants.LF:
            ch = self.reader.read()
            if self.first_eol is None:
                self.first_eol = Constants.CRLF

        if self.first_eol is None:
            if ch == Constants.LF:
                self.first_eol = Constants.LF
            elif ch == Constants.CR:
                self.first_eol = Constants.CR

        return ch in {Constants.LF, Constants.CR}

    def is_closed(self):
        return self.reader.is_closed()

    # emulate java's Character.isWhitespace
    def _is_whitespace(self, char):
        if isinstance(char, int):
            return False

        unicode_spaces = {'\u0020', '\u200B', '\u200C', '\u200D', '\u3000'}
        special_characters = {'\t', '\n', '\u000B', '\f', '\r', '\u001C', '\u001D', '\u001E', '\u001F'}
        
        return char in unicode_spaces or char in special_characters

    def is_whitespace(self, ch: str):
        return (not self.is_delimiter(ch)) and (self._is_whitespace(ch))

    def is_start_of_line(self, ch: int):
        return ch in {Constants.LF, Constants.CR, Constants.UNDEFINED}

    def is_end_of_file(self, ch: int):
        return ch == Constants.END_OF_STREAM

    def is_delimiter(self, ch: int):
        return ch == self.delimiter

    def is_escape(self, ch: int):
        return ch == self.escape

    def is_quote_char(self, ch: int):
        return ch == self.quote_char

    def is_comment_start(self, ch: int):
        return ch == self.comment_start

    def is_meta_char(self, ch: int):
        return ch in (self.delimiter,
                      self.escape,
                      self.quote_char,
                      self.comment_start
                      )

    def close(self):
        self.reader.close()
