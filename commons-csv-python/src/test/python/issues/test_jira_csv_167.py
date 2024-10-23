from pathlib import Path
from main.python.csv_format import CSVFormat
from main.python.quote_mode import QuoteMode

BASE = Path(__file__).parent.parent.parent / "resources"
class TestJiraCsv167:
  
  def get_test_input(self):
    return open(str(BASE) +
                "/csv-167/sample1.csv")

  def test_parse(self):
      
    totcomment = 0
    totrecs = 0

    with self.get_test_input() as br:
      s = None
      last_was_comment = False
      while True:
        s = br.readline()
        if not s:
          break
        if s.startswith('#'):
          if not last_was_comment:
            totcomment += 1
          last_was_comment = True
        else:
          totrecs += 1
          last_was_comment = False

    format = CSVFormat.DEFAULT

    format = format.with_allow_missing_column_names(False)
    format = format.with_comment_marker('#')
    format = format.with_delimiter(',')
    format = format.with_escape('\\')
    format = format.with_header("author", "title", "publishDate")
    format = format.with_header_comments("headerComment")
    format = format.with_null_string("NULL")
    format = format.with_ignore_empty_lines(True)
    format = format.with_ignore_surrounding_spaces(True)
    format = format.with_quote('"')
    format = format.with_quote_mode(QuoteMode.ALL)
    format = format.with_record_separator('\n')
    format = format.with_skip_header_record(False)

    comments = 0
    records = 0

    with format.parse(self.get_test_input()) as parser:
      for csv_record in parser:
        records += 1
        if csv_record.has_comment():
          comments += 1

    assert totcomment == comments
    assert totrecs == records
