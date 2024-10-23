from main.python.string_writer import StringWriter
from main.python.csv_format import CSVFormat

class TestJiraCsv164:
  def test_jira_csv_154_with_comment_marker(self):
    comment = "This is a header comment"
    format = CSVFormat.EXCEL.with_header("H1", "H2").with_comment_marker("#").with_header_comments(comment)
    out = StringWriter()
    with format.print(out) as printer:
      printer.print("A")
      printer.print("B")
    s = out.getvalue()
    assert comment in s
    
  def test_jira_csv_154_with_header_comments(self):
    comment = "This is a header comment"
    format = CSVFormat.EXCEL.with_header("H1", "H2").with_header_comments(comment).with_comment_marker("#")
    out = StringWriter()
    with format.print(out) as printer:
      printer.print("A")
      printer.print("B")
    s = out.getvalue()
    assert comment in s
