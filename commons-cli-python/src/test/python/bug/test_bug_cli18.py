import pytest
from io import StringIO
from main.python.option import Option
from main.python.options import Options
from main.python.help_formatter import HelpFormatter

class TestBugCLI18:

    def test_cli18(self):
        options = Options()
        options.add_option(Option("a", "aaa", False, "aaaaaaa"))
        options.add_option(Option(None, "bbb", False, "bbbbbbb dksh fkshd fkhs dkfhsdk fhskd hksdks dhfowehfsdhfkjshf skfhkshf sf jkshfk sfh skfh skf f"))
        options.add_option(Option("c", None, False, "ccccccc"))

        formatter = HelpFormatter()
        out = StringIO()

        formatter.print_help(pw=out, width=80, cmd_line_syntax="foobar",
            header="dsfkfsh kdh hsd hsdh fkshdf ksdh fskdh fsdh fkshfk sfdkjhskjh fkjh fkjsh khsdkj hfskdhf skjdfh ksf khf s", options=options, left_pad=2, desc_pad=2,
            footer="blort j jgj j jg jhghjghjgjhgjhg jgjhgj jhg jhg hjg jgjhghjg jhg hjg jhgjg jgjhghjg jg jgjhgjgjg jhg jhgjh" + '\r' + '\n' + "rarrr", auto_usage=True)
