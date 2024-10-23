from urllib.parse import urlparse, ParseResult
from pathlib import Path
from collections.abc import Iterator
from io import StringIO, IOBase, TextIOWrapper
from main.python.extended_buffered_reader import ExtendedBufferedReader
from main.python.token import Token
from main.python.constants import Constants
from main.python.csv_record import CSVRecord
from main.python.closeable import Closeable
from main.python.case_sensitive_dict import CaseInsensitiveDict
from main.python.java_handler import java_handler


@java_handler
class CSVParser(Closeable):
    def __init__(self, reader, format, character_offset=0, record_number=1, from_java=False):
        """
        Customized CSV parser using the given CSVFormat.

        If you do not read all records from the given reader, you should call 
        close() on the parser, unless you close the reader.

        :param reader: A Reader containing CSV-formatted input. Must not be None.
        :param format: The CSVFormat used for CSV parsing. Must not be None.
        :param character_offset: Lexer offset when the parser does not start 
            parsing at the beginning of the source.
        :param record_number: The next record number to assign.
        :raises ValueError: If the reader or format is None.
        :raises IOError: If there is a problem initializing the CSV parser.
        """
        from main.python.lexer import Lexer

        try:
            assert reader is not None
            assert format is not None
        except:
            raise ValueError("reader and format must not be None")

        self.record_list = []
        self.character_offset = character_offset
        self.reusable_token = Token()
        self.record_number = record_number - 1
        self.header_map = {}
        
        self.format = format
        self.lexer = Lexer(format, ExtendedBufferedReader(reader, from_java))
        self.csv_record_iterator = CSVParser.CSVRecordIterator(self)
        self.header_map = self.initialize_header()
        
    @staticmethod
    def parse(*args):
        if len(args) == 2:
            return CSVParser._parse1(*args)
        return CSVParser._parse2(*args)
    
    @staticmethod
    def _parse1(input_source, format):
        try:
            assert input_source is not None
            assert format is not None
        except:
            raise ValueError("input_source and format must not be None")
        
        if isinstance(input_source, str):
            return CSVParser(StringIO(input_source), format)
        elif isinstance(input_source, (StringIO, TextIOWrapper)):
            return CSVParser(input_source, format)
        
        raise ValueError("Invalid Inputs")        
    
    @staticmethod
    def _parse2(input_source, charset, csv_format):
        try:
            # Check input_source type
            assert isinstance(input_source, (Path, IOBase, str, ParseResult))
            "input_source must be a pathlib.Path object, an IOBase object, a CSV-formatted string, or a URL"

            # Check charset type
            assert isinstance(charset, str), "charset must be a string"
        except:
            raise ValueError("Invalid input_source or charset")
        
        if isinstance(input_source, Path):
            if not input_source.is_file():
                raise ValueError("file must be an existing file")
            reader = input_source.open(mode='r', encoding=charset)
        elif isinstance(input_source, IOBase):
            reader = input_source
        elif isinstance(input_source, str):
            reader = StringIO(input_source)
        elif isinstance(input_source, ParseResult):
            url = input_source.geturl()
            if url.startswith("file://"):
                path = Path(urlparse(url).path)
            else:
                raise ValueError("URL must be a file URL")
                
            reader = open(path, mode='r', encoding=charset)
        else:
            raise ValueError("input_source must be a pathlib.Path object,"
                            "an IOBase object, or a CSV-formatted string")

        if isinstance(input_source, Path):
            # Example 1: Parsing from a file path
            with input_source.open(mode='r', encoding=charset) as csv_file:
                return CSVParser(csv_file, csv_format)
        elif isinstance(input_source, IOBase):
            # Example 2: Parsing from an input stream
            return CSVParser(input_source, csv_format)
        elif isinstance(input_source, str):
            # Example 3: Parsing from a CSV string
            return CSVParser(StringIO(input_source), csv_format)

        return CSVParser(reader, csv_format)

    def add_record_value(self, last_record):
        input_content = self.reusable_token.get_content()
        input_clean = input_content.strip() if self.format.trim else input_content
        if last_record and input_clean == "" and self.format.get_trailing_delimiter():
            return
        null_string = self.format.null_string
        self.record_list.append(None if input_clean == null_string else input_clean)

    def close(self):
        """
        Closes resources.

        :raises IOError: If an I/O error occurs
        """
        if self.lexer != None:
            self.lexer.close()

    def get_current_line_number(self):
        """
        Returns the current line number in the input stream.

        ATTENTION: If your CSV input has multi-line values, the returned number does not 
                   correspond to the record number.

        :return: Current line number
        """
        return self.lexer.get_current_line_number()

    def get_first_end_of_line(self):
        """
        Gets the first end-of-line string encountered.

        :return: The first end-of-line string
        """
        return self.lexer.get_first_eol()

    def get_header_map(self):
        """
        Returns a copy of the header map that iterates in column order.

        The map keys are column names. The map values are 0-based indices.

        :return: a copy of the header map that iterates in column order.
        """
        return self.header_map.copy() if self.header_map else None

    def get_record_number(self):
        """
        Returns the current record number in the input stream.

        ATTENTION: If your CSV input has multi-line values, the returned number does not 
                   correspond to the line number.

        :return: Current record number
        """
        return self.record_number

    def get_records(self):
        """
        Parses the CSV input according to the given format and returns the 
        content as a list of CSVRecords.

        The returned content starts at the current parse-position in the stream.

        :return: List of CSVRecords, may be empty
        :raises IOError: On parse error or input read-failure
        """
        records = []
        try:
            while True:
                rec = self.next_record()
                if rec is None:
                    break
                records.append(rec)
        except IOError as e:
            # Handle any IO error that may occur during parsing
            raise IOError(f"Error parsing CSV data: {e}")
        
        return records

    def initialize_header(self):
        """
        Initializes the name to index mapping if the format defines a header.

        :return: None if the format has no header, otherwise a dictionary mapping 
                 column names to their 0-based indices.
        :raises IOError: If there is a problem reading the header or skipping the first record
        """
        hdr_map = None
        format_header = self.format.get_header()
        if format_header is not None:
            hdr_map = CaseInsensitiveDict() if self.format.get_ignore_header_case() else dict()
            header_record = None
            if len(format_header) == 0:
                # Read the header from the first line of the file
                next_record = self.next_record()
                if next_record is not None:
                    header_record = next_record.values()
            else:
                if self.format.get_skip_header_record():
                    self.next_record()
                header_record = format_header

            # Build the name to index mappings
            if header_record is not None:
                for i, header in enumerate(header_record):
                    contains_header = header in hdr_map
                    empty_header = header is None or header.strip() == ''
                    if (contains_header and 
                        (not empty_header or not self.format.get_allow_missing_column_names())):
                        raise ValueError(f"The header contains a duplicate name"
                                         f": \"{header}\" in {header_record}")
                    hdr_map[header] = i

        return hdr_map

    def is_closed(self):
        """
        Gets whether this parser is closed.

        :return: True if this parser is closed, False otherwise.
        """
        return self.lexer.is_closed()
    
    def __iter__(self):
        """
        Returns an iterator on the records.

        An IOError caught during the iteration is re-thrown as an RuntimeError.
        If the parser is closed, a call to `next()` will raise a StopIteration.

        :return: Iterator for CSVRecords
        """
        return self.csv_record_iterator
    
    def iterator(self):
        return iter(self)
    
    class CSVRecordIterator(Iterator):
        def __init__(self, csv_parser):
            self.csv_parser = csv_parser
            self.current = None

        def get_next_record(self):
            try:
                return self.csv_parser.next_record()
            except StopIteration:
                return None

        def has_next(self):
            if self.csv_parser.is_closed():
                return False
            if self.current is None:
                self.current = self.get_next_record()
            return self.current is not None

        def __next__(self):
            if self.csv_parser.is_closed():
                raise StopIteration("CSVParser has been closed")
            next_record = self.current
            self.current = None
            if next_record is None:
                next_record = self.get_next_record()
                if next_record is None:
                    raise StopIteration("No more CSV records available")
            return next_record

        def remove(self):
            raise NotImplementedError("remove() method is not supported")
        
    def next_record(self):
        self.record_list.clear()
        sb = None   
        result = None
        start_char_position = self.lexer.get_character_position() + self.character_offset

        while True:
            self.reusable_token.reset()
            self.lexer.next_token(self.reusable_token)

            if self.reusable_token.get_type() == Token.Type.TOKEN:
                self.add_record_value(False)
            elif self.reusable_token.get_type() == Token.Type.EORECORD:
                self.add_record_value(True)
                break
            elif self.reusable_token.get_type() == Token.Type.EOF:
                if self.reusable_token.is_ready:
                    self.add_record_value(True)
                break
            elif self.reusable_token.get_type() == Token.Type.INVALID:
                raise IOError(f"(line {self.get_current_line_number()}) invalid parse sequence")
            elif self.reusable_token.get_type() == Token.Type.COMMENT:
                if sb is None:
                    sb = []
                else:
                    sb.append(Constants.LF)
                sb.append(self.reusable_token.get_content())
                self.reusable_token.set_type(Token.Type.TOKEN)  # Read another token
            else:
                raise ValueError(f"Unexpected Token type: {self.reusable_token.get_type()}")
            
            if self.reusable_token.get_type() != Token.Type.TOKEN:
                break

        if self.record_list:
            self.record_number += 1
            comment = "".join(sb) if sb else None
            result = CSVRecord(self.record_list[:], self.header_map, comment, 
                               self.record_number, start_char_position)

        return result
