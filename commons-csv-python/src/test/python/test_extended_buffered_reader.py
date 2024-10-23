import io
import pytest
from main.python.extended_buffered_reader import ExtendedBufferedReader
from main.python.constants import Constants


class TestExtendedBufferedReader:

    def create_buffered_reader(self, s: str):
        return ExtendedBufferedReader(io.StringIO(s))

    def test_empty_input(self):
        with self.create_buffered_reader("") as br:
            assert br.read() == Constants.END_OF_STREAM
            assert br.look_ahead() == Constants.END_OF_STREAM
            assert br.get_last_char() == Constants.END_OF_STREAM
            assert br.read_line() is None
            assert br.read([None], 0, 0) == 0

    def test_read_lookahead1(self):
        with self.create_buffered_reader("1\n2\r3\n") as br:
            assert br.get_current_line_number() == 0
            assert br.look_ahead() == '1'
            assert br.get_last_char() == Constants.UNDEFINED
            assert br.get_current_line_number() == 0
            assert br.read() == '1'  # Start line 1
            assert br.get_last_char() == '1'

            assert br.get_current_line_number() == 1
            assert br.look_ahead() == '\n'
            assert br.get_current_line_number() == 1
            assert br.get_last_char() == '1'
            assert br.read() == '\n'
            assert br.get_current_line_number() == 1
            assert br.get_last_char() == '\n'
            assert br.get_current_line_number() == 1

            assert br.look_ahead() == '2'
            assert br.get_current_line_number() == 1
            assert br.get_last_char() == '\n'
            assert br.get_current_line_number() == 1
            assert br.read() == '2'  # Start line 2
            assert br.get_current_line_number() == 2
            assert br.get_last_char() == '2'

            assert br.look_ahead() == '\r'
            assert br.get_current_line_number() == 2
            assert br.get_last_char() == '2'
            assert br.read() == '\r'
            assert br.get_last_char() == '\r'
            assert br.get_current_line_number() == 2

            assert br.look_ahead() == '3'
            assert br.get_last_char() == '\r'
            assert br.read() == '3'  # Start line 3
            assert br.get_last_char() == '3'
            assert br.get_current_line_number() == 3

            assert br.look_ahead() == '\n'
            assert br.get_current_line_number() == 3
            assert br.get_last_char() == '3'
            assert br.read() == '\n'
            assert br.get_current_line_number() == 3
            assert br.get_last_char() == '\n'
            assert br.get_current_line_number() == 3

            assert br.look_ahead() == Constants.END_OF_STREAM
            assert br.get_last_char() == '\n'
            assert br.read() == Constants.END_OF_STREAM
            assert br.get_last_char() == Constants.END_OF_STREAM
            assert br.read() == Constants.END_OF_STREAM
            assert br.look_ahead() == Constants.END_OF_STREAM
            assert br.get_current_line_number() == 3

    def test_read_lookahead2(self):
        ref = [None] * 5
        res = [None] * 5
        with self.create_buffered_reader("abcdefg") as br:
            ref[0] = 'a'
            ref[1] = 'b'
            ref[2] = 'c'
            assert br.read(res, 0, 3) == 3
            assert ref == res
            assert br.get_last_char() == 'c'

            assert br.look_ahead() == 'd'
            ref[4] = 'd'
            assert br.read(res, 4, 1) == 1
            assert ref == res
            assert br.get_last_char() == 'd'

    def test_read_line(self):
        with self.create_buffered_reader("") as br:
            assert br.read_line() is None

        with self.create_buffered_reader("\n") as br:
            assert br.read_line() == ""
            assert br.read_line() is None

        with self.create_buffered_reader("foo\n\nhello") as br:
            assert br.get_current_line_number() == 0
            assert br.read_line() == "foo"
            assert br.get_current_line_number() == 1
            assert br.read_line() == ""
            assert br.get_current_line_number() == 2
            assert br.read_line() == "hello"
            assert br.get_current_line_number() == 3
            assert br.read_line() is None
            assert br.get_current_line_number() == 3

        with self.create_buffered_reader("foo\n\nhello") as br:
            assert br.read() == "f"
            assert br.look_ahead() == "o"
            assert br.read_line() == "oo"
            assert br.look_ahead() == "\n"
            assert br.read_line() == ""
            assert br.get_current_line_number() == 2
            assert br.look_ahead() == "h"
            assert br.read_line() == "hello"
            assert br.read_line() is None
            assert br.get_current_line_number() == 3

        with self.create_buffered_reader("foo\rbaar\r\nfoo") as br:
            assert br.read_line() == "foo"
            assert br.look_ahead() == "b"
            assert br.read_line() == "baar"
            assert br.look_ahead() == "f"
            assert br.read_line() == "foo"
            assert br.read_line() is None

    def test_read_char(self):
        LF = "\n"
        CR = "\r"
        CRLF = CR + LF
        LFCR = LF + CR
        test = (
            "a" + LF + "b" + CR + "c" + LF + LF + "d" + CR + CR +
            "e" + LFCR + "f " + CRLF
        )
        EOLeolct = 9

        with self.create_buffered_reader(test) as br:
            assert br.get_current_line_number() == 0
            while br.read_line() is not None:
                pass
            assert br.get_current_line_number() == EOLeolct

        with self.create_buffered_reader(test) as br:
            assert br.get_current_line_number() == 0
            while br.read() != -1:
                pass
            assert br.get_current_line_number() == EOLeolct

        with self.create_buffered_reader(test) as br:
            assert br.get_current_line_number() == 0
            buff = [None] * 10
            while br.read(buff, 0, 3) != -1:
                pass
            assert br.get_current_line_number() == EOLeolct
