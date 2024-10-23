from main.python.closeable import Closeable
from main.python.java_handler import Types, java_handler

@java_handler
class CSVPrinter(Closeable):
    CR = "\r"
    LF = "\n"
    SP = " "

    def __init__(self, out, format):
        try:
            assert out is not None
            assert format is not None
        except:
            raise ValueError("out and format must not be None")

        self.out = out
        self.format = format
        self.new_record = True
        if format.get_header_comments():
            for line in format.get_header_comments():
                if line is not None:
                    self.print_comment(line)
        if format.get_header() and not format.get_skip_header_record():
            self.print_record(*format.get_header())

    def close(self, flush=False):
        if flush or self.format.get_auto_flush():
            if hasattr(self.out, "flush"):
                self.out.flush()
        if hasattr(self.out, "close"):
            self.out.close()

    def flush(self):
        if hasattr(self.out, "flush"):
            self.out.flush()

    def get_out(self):
        return self.out

    def print(self, value):
        self.format.print(value, self.out, self.new_record)
        self.new_record = False

    def _append(self, appendable, string):
        if hasattr(appendable, "append"):
            try: appendable.append(string)
            except: appendable.append(string.encode("utf-8"))
        else:
            try: appendable.write(string)
            except: appendable.write(string.encode("utf-8"))

    def print_comment(self, comment):
        if not self.format.is_comment_marker_set():
            return
        if not self.new_record:
            self.println()
        self._append(self.out, self.format.get_comment_marker())
        self._append(self.out, self.SP)
        for i in range(len(comment)):
            c = comment[i]
            if c == self.CR:
                if i + 1 < len(comment) and comment[i + 1] == self.LF:
                    i += 1
                self.println()
                self._append(self.out, self.format.get_comment_marker())
                self._append(self.out, self.SP)
            elif c == self.LF:
                self.println()
                self._append(self.out, self.format.get_comment_marker())
                self._append(self.out, self.SP)
            else:
                self._append(self.out, c)
        self.println()

    def println(self):
        self.format.println(self.out)
        self.new_record = True

    def __check_all_strings(self, *values):
        if values is None:
            return False

        for value in values:
            if not isinstance(value, str):
                return False
        return True

    def print_record(self, *values):        
        if len(values) == 1 and \
                hasattr(values[0], "__iter__") and \
                not isinstance(values[0], str): # check if values[0] is iterable but is not a string!
            for value in values[0]:
                self.print(value)
            self.println()
        else:
            self.format.print_record(self.out, *values)
            self.new_record = True

    def print_records(self, *values):      
        if len(values) == 1 and isinstance(values[0], Types.Cursor):
            return self.print_records_result_set(values[0])
        
        for value in values:            
            value = value if value != None else []
            
            # check if value is a list of records
            if self.__check_all_strings(*value):
                self.print_record(*value)
            else:
                # value is a list of lists/iterables
                for record in value:
                    formatted_value = record if record != None else []
                    self.print_record(*formatted_value)

    def print_records_result_set(self, result_set):
        # result_set is java.sql.ResultSet
        if hasattr(result_set, "next"):
            column_count = result_set.getMetaData().getColumnCount()
            while result_set.next():
                for i in range(1, column_count+1):
                    self.print(result_set.getObject(i))
                self.println()
        # result_set is python iterable
        else:
            for line in result_set:
                for e in line:
                    self.print(e)
                self.println()
