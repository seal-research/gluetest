import pytest
from io import StringIO
from main.python.token import Token
from main.python.constants import Constants
from main.python.extended_buffered_reader import ExtendedBufferedReader
from main.python.lexer import Lexer
from main.python.csv_format import CSVFormat
from test.python.token_matchers import TokenMatchers
from hamcrest import assert_that


class TestLexer:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.format_with_escaping = (
            CSVFormat.DEFAULT.with_escape('\\')
        )

    def create_lexer(self, input_str: str, csv_format: CSVFormat):
        buffer_reader = ExtendedBufferedReader(StringIO(input_str))
        return Lexer(csv_format, buffer_reader)

    def test_surrounding_spaces_are_deleted(self):
        code = "noSpaces,  leadingSpaces,trailingSpaces  \
            ,  surroundingSpaces  ,  ,,"
        with self.create_lexer(
                code,
                CSVFormat.DEFAULT.with_ignore_surrounding_spaces()
                                     ) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "noSpaces"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "leadingSpaces"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "trailingSpaces"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN,
                                                  "surroundingSpaces"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))

    def test_surrounding_tabs_are_deleted(self):
        code = "noTabs,\tleadingTab,trailingTab\t,\tsurroundingTabs\t,\t\t,,"
        with self.create_lexer(code,
                                    CSVFormat.DEFAULT
                                    .with_ignore_surrounding_spaces()
                                    ) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "noTabs"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "leadingTab"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "trailingTab"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.TOKEN, "surroundingTabs")
                                                  )
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))

    def test_ignore_empty_lines(self):
        code = ("first,line,\n" + "\n"
                + "\n" + "second,line\n"
                + "\n" + "\n" + "third line \n" + "\n" +
                "\n" + "last, line \n" + "\n" + "\n" + "\n")
        formatter = CSVFormat.DEFAULT.with_ignore_empty_lines()
        with self.create_lexer(code, formatter) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "first"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "line"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "second"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "line"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "third line "
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "last"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, " line "
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))

    def test_comments(self):
        code = (
            "first,line,\n" +
            "second,line,tokenWith#no-comment\n"
            + "# comment line \n" + "third,line,#no-comment\n"
            + "# penultimate comment\n" + "# Final comment\n")
        formatter = CSVFormat.DEFAULT.with_comment_marker('#')
        with self.create_lexer(code, formatter) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "first"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "line"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "second"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "line"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.EORECORD,   "tokenWith#no-comment"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.COMMENT, "comment line"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "third"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "line"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "#no-comment"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.COMMENT, "penultimate comment"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.COMMENT, "Final comment"
                ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))

    def test_comments_and_empty_lines(self):
        code = ("1,2,3,\n" + "\n"
                + "\n" + "a,b x,c#no-comment\n" + "#foo\n" + "\n" +
                "\n" + "d,e,#no-comment\n"
                + "\n" + "\n" + "# penultimate comment\n" +
                "\n" + "\n" + "# Final comment\n")
        formatter = (
            CSVFormat.DEFAULT.with_comment_marker('#')
            .with_ignore_empty_lines(False)
            )
        assert not formatter.get_ignore_empty_lines()

        with self.create_lexer(code, formatter) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "1"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "2"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "3"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "b x"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.EORECORD, "c#no-comment"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.COMMENT, "foo"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "d"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "e"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.EORECORD, "#no-comment"
                ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.COMMENT, "penultimate comment"))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.COMMENT, "Final comment"
                ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))

    def test_backslash_without_escaping(self):
        code = "a,\\,,b\\\n\\,,"
        formatter = CSVFormat.DEFAULT
        assert not formatter.is_escape_character_set()
        with self.create_lexer(code, formatter) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "\\"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "b\\"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "\\"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, ""
                                                  ))

    def test_backslash_with_escaping(self):
        code = "a,\\,,b\\\\\n\\,,\\\nc,d\\\r\ne"
        formatter = (
            self.format_with_escaping.with_ignore_empty_lines(False)
            )
        assert formatter.is_escape_character_set()
        with self.create_lexer(code, formatter) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ","
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "b\\"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ","
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "\nc"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "d\r"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, "e"
                                                  ))

    def test_next_token4(self):
        code = ("a,\"foo\",b\na,   "
                "\" foo\",b\na,\"foo \"  "
                ",b\na,  \" foo \"  ,b")
        with self.create_lexer(
            code, CSVFormat.DEFAULT.with_ignore_surrounding_spaces()
                ) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "foo"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "b"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, " foo"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "b"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "foo "
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "b"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, " foo "
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, "b"
                                                  ))

    def test_next_token5(self):
        code = "a,\"foo\n\",b\n\"foo\n  baar ,,,\"\n\"\n\t \n\""
        with self.create_lexer(code, CSVFormat.DEFAULT) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "foo\n"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EORECORD, "b"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.EORECORD, "foo\n  baar ,,,"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, "\n\t \n"
                                                  ))

    def test_next_token6(self):
        code = "a;'b and '' more\n'\n!comment;;;;\n;;"
        formatter = (
            CSVFormat.DEFAULT.with_quote('\'')
            .with_comment_marker('!').with_delimiter(';')
            )
        with self.create_lexer(code, formatter) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "a"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(
                Token.Type.EORECORD, "b and ' more\n"))

    def test_delimiter_is_whitespace(self):
        code = "one\ttwo\t\tfour \t five\t six"
        with self.create_lexer(code, CSVFormat.TDF) as parser:
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "one"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "two"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, ""
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "four"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.TOKEN, "five"
                                                  ))
            assert_that(parser.next_token(
                Token()), TokenMatchers.matches(Token.Type.EOF, "six"
                                                  ))

    def test_escaped_cr(self):
        with self.create_lexer(
            "character\\" + Constants.CR + "Escaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                "character" + Constants.CR + "Escaped"
                                                  ))

    def test_cr(self):
        with self.create_lexer(
            "character" + Constants.CR
            + "NotEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()),TokenMatchers.has_content("character"
                                                  ))
            assert_that(lexer.next_token(
                Token()),TokenMatchers.has_content("NotEscaped"
                                                  ))

    def test_escaped_lf(self):
        with self.create_lexer(
            "character\\" + Constants.LF
            + "Escaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.LF + "Escaped"
                    ))

    def test_lf(self):
        with self.create_lexer(
            "character" + Constants.LF
            + "NotEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content("character"))
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content("NotEscaped"))

    def test_escaped_tab(self):
        with self.create_lexer(
            "character\\" + Constants.TAB
            + "Escaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.TAB + "Escaped"
                    ))

    def test_tab(self):
        with self.create_lexer(
            "character" + Constants.TAB
            + "NotEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.TAB + "NotEscaped"
                    ))

    def test_escaped_backspace(self):
        with self.create_lexer(
            "character\\" + Constants.BACKSPACE
            + "Escaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.BACKSPACE + "Escaped"
                    ))

    def test_backspace(self):
        with self.create_lexer(
            "character" + Constants.BACKSPACE
            + "NotEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.BACKSPACE + "NotEscaped"
                    ))

    def test_escaped_ff(self):
        with self.create_lexer(
            "character\\" + Constants.FF
            + "Escaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.FF + "Escaped"
                    ))

    def test_ff(self):
        with self.create_lexer(
            "character" + Constants.FF
            + "NotEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.FF + "NotEscaped"
                    ))

    def test_escaped_mysql_null_value(self):
        with self.create_lexer(
            "character\\NEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character\\NEscaped"
                    ))

    def test_escaped_character(self):
        with self.create_lexer(
            "character\\aEscaped", self.format_with_escaping
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character\\aEscaped"
                    ))

    def test_escaped_control_character(self):
        with self.create_lexer(
            "character!rEscaped", CSVFormat.DEFAULT.with_escape('!')
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                        "character" + Constants.CR + "Escaped"
                    ))

    def test_escaped_control_character2(self):
        with self.create_lexer(
            "character\\rEscaped", CSVFormat.DEFAULT.with_escape('\\')
                ) as lexer:
            assert_that(lexer.next_token(
                Token()), TokenMatchers.has_content(
                    "character" + Constants.CR + "Escaped"
                    ))

    def test_escaping_at_eof(self):
        code = "escaping at Token.Type.EOF is evil\\"
        with self.create_lexer(
                code, self.format_with_escaping
        ) as lexer:
            with pytest.raises(IOError):
                lexer.next_token(Token())
