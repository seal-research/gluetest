import io
from types import MethodType
from main.python.constants import Constants
from main.python.java_handler import Types


class ExtendedBufferedReader(io.StringIO):
    def __init__(self, reader, from_java=False):
        self._last_char = Constants.UNDEFINED
        self._eol_counter = 0
        self._position = 0
        self._closed = False
        self.mark = None
        self._write_pos = 0
        self.from_java = from_java
        
        # init super class based on callee environment
        if self.from_java:
            self.reader = reader
            self.buffered_reader = Types.BufferedReader(reader)
        else:
            super().__init__(reader.read())
            __write = reader.write
            def _write(this, s: str) -> int:
                self.seek(self._write_pos)
                self.write(s)
                self._write_pos = self.tell()
                self.seek(self._position)
                return __write(s)
            reader.write = MethodType(_write, reader)
            self.reader = None
            self.buffered_reader = None

    def _readline_python(self, length=-1):
        initial_pos = self.tell()
        value = super().readline(length)

        if not value:
            return None

        offset = 0
        if value.endswith("\r\n"):
            value = value[:-2]
            offset = 2
        if value.endswith(("\r", "\n")):
            value = value[:-1]
            offset = 1
            
        min_break = len(value)
        if "\r" in value and value.index("\r") < min_break:
            min_break = value.index("\r")
            offset = 1
        if "\n" in value and value.index("\n") < min_break:
            min_break = value.index("\n")
            offset = 1
        if "\r\n" in value and value.index("\r\n") <= min_break:
            min_break = value.index("\r\n")
            offset = 2

        s = value[:min_break]
        self.seek(initial_pos + len(s) + offset)
        return s

    def _readline(self, length=-1):
        if self.from_java:
            return self.buffered_reader.readLine()
        else:
            return self._readline_python(length)
    
    def _read(self, length=None):
        if self.from_java:
            char_int = self.buffered_reader.read()
            return chr(char_int) if char_int != -1 else Constants.END_OF_STREAM
        else:
            value = super().read(length)
            return value if value else Constants.END_OF_STREAM

    def read(self, *args):
        if len(args) == 0:
            current = self._read(1)
            if current == Constants.CR or (current == Constants.LF and self._last_char != Constants.CR):
                self._eol_counter += 1
            self._last_char = current
            self._position += 1
            return self._last_char      
        if len(args) == 3:
            buf, offset, length = args
            i = 0
            c = self.read()
            if c == Constants.END_OF_STREAM and length > 0:
                return Constants.END_OF_STREAM
            
            while i < length and c != Constants.END_OF_STREAM:
                buf[offset + i] = c
                i += 1
                if i < length:
                    c = self.read()
            return i

    def get_last_char(self):
        return self._last_char

    def read_extended(self, length=None):
        if length == 0:
            return 0

        buf = super().read(length)

        if buf:
            for ch in buf:
                if ch == Constants.LF:
                    if self._last_char != Constants.CR:
                        self._eol_counter += 1
                elif ch == Constants.CR:
                    self._eol_counter += 1

            self._last_char = buf[-1]

        elif buf == "":
            self._last_char = Constants.END_OF_STREAM

        self._position += len(buf)
        return len(buf)

    def read_line(self):
        line = self._readline()
        if line or line == "":
            self._last_char = Constants.LF
            self._eol_counter += 1
        else:
            self._last_char = Constants.END_OF_STREAM
        return line

    def look_ahead(self):
        if self.from_java:
            self.buffered_reader.mark(1)
        else: 
            self.mark = self.tell()
        
        c = self._read(1)
        self.reset()

        return c
    
    def reset(self):
        if self.from_java:
            self.buffered_reader.reset()
        else:
            if self.mark == None:
                raise IOError("Mark not set")
            self.seek(self.mark)        

    def get_current_line_number(self):
        if (
            self._last_char == Constants.CR
            or self._last_char == Constants.LF
            or self._last_char == Constants.UNDEFINED
            or self._last_char == Constants.END_OF_STREAM
        ):
            return self._eol_counter
        return self._eol_counter + 1

    def get_position(self):
        return self._position

    def is_closed(self):
        return self._closed

    def close(self):
        self._closed = True
        self._last_char = Constants.END_OF_STREAM
        if self.from_java:
            self.buffered_reader.close()
            self.reader.close()
        else:
            super().close()
