import pytest
import os
from io import StringIO
from main.python.help_formatter import HelpFormatter
from main.python.option import Option
from main.python.options import Options
from main.python.option_group import OptionGroup

class TestHelpFormatter:
    
    def setup_method(self):
        self.eol = os.linesep
    
    def test_accessors(self):
        formatter = HelpFormatter()
        
        formatter.set_arg_name("argname")
        assert formatter.get_arg_name() == "argname", "arg name"

        formatter.set_desc_padding(3) 
        assert formatter.get_desc_padding() == 3, "desc padding"

        formatter.set_left_padding(7)
        assert formatter.get_left_padding() == 7, "left padding"

        formatter.set_long_opt_prefix("~~")
        assert formatter.get_long_opt_prefix() == "~~", "long opt prefix"

        formatter.set_new_line("\n")
        assert formatter.get_new_line() == "\n", "new line"
        
        formatter.set_opt_prefix("~")
        assert formatter.get_opt_prefix() == "~", "opt prefix"

        formatter.set_syntax_prefix("-> ")
        assert formatter.get_syntax_prefix() == "-> ", "syntax prefix"

        formatter.set_width(80)
        assert formatter.get_width() == 80, "width"
    
    def test_automatic_usage(self):
        hf = HelpFormatter()
        pw = StringIO()
        
        # Test case with one option
        option_a = Option.builder("a").desc("aaaa aaaa aaaa aaaa aaaa").build()
        options = Options().add_option(option_a)
        expected = "usage: app [-a]"
        hf.print_usage(pw, 60, app="app", options=options)
        assert expected == pw.getvalue().strip(), "simple auto usage"
        pw.truncate(0)
        pw.seek(0)

        # Test case with two options
        option_b = Option.builder("b").desc("bbb").build()
        options = Options().add_option(option_a).add_option(option_b)
        expected = "usage: app [-a] [-b]"
        hf.print_usage(pw, 60, app="app", options=options)
        assert expected == pw.getvalue().strip(), "simple auto usage"
        pw.truncate(0)
        pw.seek(0)

    def test_default_arg_name(self):
        option = Option.builder("f").has_arg().required(True).build()
        options = Options()
        options.add_option(option)

        out = StringIO()
        formatter = HelpFormatter()
        
        formatter.set_arg_name("argument")
        formatter.print_usage(out, 80, app="app", options=options)

        assert "usage: app -f <argument>" + self.eol == out.getvalue()

    def test_find_wrap_pos(self):
        hf = HelpFormatter()
        
        text = "This is a test."
        assert hf.find_wrap_pos(text, 8, 0) == 7
        assert hf.find_wrap_pos(text, 8, 8) == -1

        text = "aaaa aa"
        assert hf.find_wrap_pos(text, 3, 0) == 3

        text = "aaaaaa aaaaaa"
        assert hf.find_wrap_pos(text, 6, 0) == 6
        assert hf.find_wrap_pos(text, 6, 7) == -1

        text = f"aaaaaa\n aaaaaa"
        assert hf.find_wrap_pos(text, 6, 0) == 7

        text = "aaaaaa\t aaaaaa"
        assert hf.find_wrap_pos(text, 6, 0) == 7
    
    def test_header_starting_with_line_separator(self):
        options = Options()
        formatter = HelpFormatter()
        header = f"{self.eol}Header"
        footer = "Footer"
        out = StringIO()
        formatter.print_help(cmd_line_syntax="foobar", options=options, pw=out, width=80, header=header, left_pad=2, desc_pad=2, footer=footer, auto_usage=True)
        
        expected_output = f"usage: foobar{self.eol}{self.eol}Header{self.eol}{self.eol}Footer{self.eol}"
        
        assert out.getvalue() == expected_output
    
    def test_help_with_long_opt_separator(self):
        # Create options
        options = Options()
        options.add_option("f", True, "the file")
        options.add_option(Option.builder("s").long_opt("size").desc("the size").has_arg().arg_name("SIZE").build())
        options.add_option(Option.builder().long_opt("age").desc("the age").has_arg().build())

        formatter = HelpFormatter()
        assert HelpFormatter.DEFAULT_LONG_OPT_SEPARATOR == formatter.get_long_opt_separator()
        formatter.set_long_opt_separator("=")
        assert "=" == formatter.get_long_opt_separator()

        out = StringIO()
        
        formatter.print_help("create", options, pw=out, width=80, header="header", left_pad=2, desc_pad=2, footer="footer")
        expected_output = f"usage: create{self.eol}header{self.eol}     --age=<arg>    the age{self.eol}  -f <arg>          the file{self.eol}  -s,--size=<SIZE>  the size{self.eol}footer{self.eol}"
        
        assert out.getvalue() == expected_output


    def test_indented_header_and_footer(self):
        options = Options()
        formatter = HelpFormatter()
        header = f"  Header1{self.eol}  Header2"
        footer = f"  Footer1{self.eol}  Footer2"
        out = StringIO()
        formatter.print_help("foobar", options, pw=out, width=80, header=header, left_pad=2, desc_pad=2, footer=footer, auto_usage=True)

        expected_output = "usage: foobar" + self.eol +\
                        "  Header1" + self.eol +\
                        "  Header2" + self.eol +\
                        "" + self.eol +\
                        "  Footer1" + self.eol +\
                        "  Footer2" + self.eol

        assert out.getvalue() == expected_output
    
    def test_option_without_short_format(self):
        # Create options
        options = Options()
        options.add_option(Option("a", "aaa", False, "aaaaaaa"))
        options.add_option(Option(None, "bbb", False, "bbbbbbb"))
        options.add_option(Option("c", None, False, "ccccccc"))

        formatter = HelpFormatter()
        out = StringIO()
        formatter.print_help("foobar", options, pw=out, width=80, header="", left_pad=2, desc_pad=2, footer="", auto_usage=True)

        expected_output = "usage: foobar [-a] [--bbb] [-c]" + self.eol +\
                        "  -a,--aaa  aaaaaaa" + self.eol +\
                        "     --bbb  bbbbbbb" + self.eol +\
                        "  -c        ccccccc" + self.eol

        assert out.getvalue() == expected_output



    def test_option_without_short_format2(self):
        help = Option.builder('h').long_opt('help').desc('print this message').build()
        version = Option.builder('v').long_opt('version').desc('print version information').build()
        new_run = Option.builder('n').long_opt('new').desc('Create NLT cache entries only for new items').build()
        tracker_run = Option.builder('t').long_opt('tracker').desc('Create NLT cache entries only for tracker items').build()

        time_limit = Option.builder('l') \
            .long_opt('limit') \
            .has_arg() \
            .value_separator() \
            .desc('Set time limit for execution, in minutes') \
            .build()

        age = Option.builder('a') \
            .long_opt('age') \
            .has_arg() \
            .value_separator() \
            .desc('Age (in days) of cache item before being recomputed') \
            .build()

        server = Option.builder('s') \
            .long_opt('server') \
            .has_arg() \
            .value_separator() \
            .desc('The NLT server address') \
            .build()

        num_results = Option.builder('r') \
            .long_opt('results') \
            .has_arg() \
            .value_separator() \
            .desc('Number of results per item') \
            .build()

        config_file = Option.builder() \
            .long_opt('config') \
            .has_arg() \
            .value_separator() \
            .desc('Use the specified configuration file') \
            .build()

        options = Options()
        options.add_option(help)
        options.add_option(version)
        options.add_option(new_run)
        options.add_option(tracker_run)
        options.add_option(time_limit)
        options.add_option(age)
        options.add_option(server)
        options.add_option(num_results)
        options.add_option(config_file)

        formatter = HelpFormatter()
        out = StringIO()
        formatter.print_help('commandline', options, pw=out, width=80, header='header', left_pad=2, desc_pad=2, footer='footer', auto_usage=True)

        expected_output = "usage: commandline [-a <arg>] [--config <arg>] [-h] [-l <arg>] [-n] [-r <arg>]" + self.eol + \
                          "       [-s <arg>] [-t] [-v]" + self.eol + \
                          "header" + self.eol + \
                          "  -a,--age <arg>      Age (in days) of cache item before being recomputed" + self.eol + \
                          "     --config <arg>   Use the specified configuration file" + self.eol + \
                          "  -h,--help           print this message" + self.eol + \
                          "  -l,--limit <arg>    Set time limit for execution, in minutes" + self.eol + \
                          "  -n,--new            Create NLT cache entries only for new items" + self.eol + \
                          "  -r,--results <arg>  Number of results per item" + self.eol + \
                          "  -s,--server <arg>   The NLT server address" + self.eol + \
                          "  -t,--tracker        Create NLT cache entries only for tracker items" + self.eol + \
                          "  -v,--version        print version information" + self.eol + \
                          "footer"

        assert out.getvalue().strip() == expected_output.strip()

    def test_print_help_newline_footer(self):
        formatter = HelpFormatter()
        out = StringIO()
        # Create options
        options = Options().add_option("a", "b")

        formatter.print_help(
            pw=out,
            width=80,
            cmd_line_syntax="test" + self.eol,
            header="header" + self.eol,
            options=options,
            left_pad=0,
            desc_pad=0,
            footer=self.eol
        )

        expected = "usage: test" + self.eol +\
                "header" + self.eol +\
                "-ab" + self.eol + self.eol

        out.flush()

        assert expected == out.getvalue()

    def test_print_help_newline_header(self):
        formatter = HelpFormatter()
        out = StringIO()
        options = Options().add_option("a", "b")

        formatter.print_help(
            pw=out,
            width=80,
            cmd_line_syntax="test" + self.eol,
            header=self.eol,
            options=options,
            left_pad=0,
            desc_pad=0,
            footer="footer" + self.eol
        )

        expected = "usage: test" + self.eol + \
            self.eol + \
            "-ab" + self.eol + \
            "footer" + self.eol
        
        out.flush()
        
        assert out.getvalue() == expected, "header newline"

    def test_print_help_with_empty_syntax(self):
        formatter = HelpFormatter()
        try:
            formatter.print_help(cmd_line_syntax=None, options=Options())
            pytest.fail("None command line syntax should be rejected")
        except ValueError:
            pass

    def test_print_option_group_usage(self):
        group = OptionGroup()
        group.add_option(Option.builder("a").build())
        group.add_option(Option.builder("b").build())
        group.add_option(Option.builder("c").build())

        options = Options()
        options.add_option_group(group)
        
        out = StringIO()
        formatter = HelpFormatter()

        formatter.print_usage(pw=out, width=80, app="app", options=options)

        assert out.getvalue() == f"usage: app [-a | -b | -c]{self.eol}"

    
    def test_print_options(self):
        sb = []
        hf = HelpFormatter()
        left_pad = 1
        desc_pad = 3
        lpad = hf.create_padding(left_pad)
        dpad = hf.create_padding(desc_pad)

        options = Options().add_option("a", False, "aaaa aaaa aaaa aaaa aaaa")
        expected = lpad + "-a" + dpad + "aaaa aaaa aaaa aaaa aaaa"
        hf.render_options(sb, 60, options, left_pad, desc_pad)
        assert ''.join(sb) == expected, "simple non-wrapped option"

        next_line_tab_stop = left_pad + desc_pad + len("-a")
        expected = lpad + "-a" + dpad + "aaaa aaaa aaaa" + self.eol + hf.create_padding(next_line_tab_stop) + "aaaa aaaa"
        sb.clear()
        hf.render_options(sb, next_line_tab_stop + 17, options, left_pad, desc_pad)
        assert ''.join(sb) == expected, "simple wrapped option"

        options = Options().add_option("a", "aaa", False, "dddd dddd dddd dddd")
        expected = lpad + "-a,--aaa" + dpad + "dddd dddd dddd dddd"
        sb.clear()
        hf.render_options(sb, 60, options, left_pad, desc_pad)
        assert ''.join(sb) == expected, "long non-wrapped option"

        next_line_tab_stop = left_pad + desc_pad + len("-a,--aaa")
        expected = lpad + "-a,--aaa" + dpad + "dddd dddd" + self.eol + hf.create_padding(next_line_tab_stop) + "dddd dddd"
        sb.clear()
        hf.render_options(sb, 25, options, left_pad, desc_pad)
        assert ''.join(sb) == expected, "long wrapped option"

        options = Options().add_option("a", "aaa", False, "dddd dddd dddd dddd").add_option("b", False, "feeee eeee eeee eeee")
        expected = lpad + "-a,--aaa" + dpad + "dddd dddd" + self.eol + hf.create_padding(next_line_tab_stop) + "dddd dddd" + self.eol + lpad + "-b      " + dpad + "feeee eeee" + self.eol + hf.create_padding(next_line_tab_stop) + "eeee eeee"
        sb.clear()
        hf.render_options(sb, 25, options, left_pad, desc_pad)
        assert ''.join(sb) == expected, "multiple wrapped options"
    
    def test_print_option_with_empty_arg_name_usage(self):
        option = Option("f", True, None)
        option.set_arg_name("")
        option.set_required(True)
        
        options = Options()
        options.add_option(option)

        out = StringIO()
        formatter = HelpFormatter()
        
        formatter.print_usage(pw=out, width=80, app="app", options=options)

        assert out.getvalue() == "usage: app -f" + self.eol
    
    def test_print_required_option_group_usage(self):
        group = OptionGroup()
        group.add_option(Option.builder("a").build())
        group.add_option(Option.builder("b").build())
        group.add_option(Option.builder("c").build())
        group.set_required(True)

        options = Options()
        options.add_option_group(group)

        out = StringIO()
        formatter = HelpFormatter()
        
        formatter.print_usage(out, 80, app="app", options=options)

        assert out.getvalue() == f"usage: app -a | -b | -c{self.eol}"
    
    
    def test_print_sorted_usage(self):

        class ReversedOptionComparator(HelpFormatter.OptionComparator):
            def compare(self, opt: Option) -> str:
                # returns the negative sum of the Unicode code point for each character in the key
                return -sum(ord(ch) for ch in opt.get_key().casefold())
        
        options = Options()
        options.add_option(Option.builder("a").desc("first").build())
        options.add_option(Option.builder("b").desc("second").build())
        options.add_option(Option.builder("c").desc("third").build())

        helpFormatter = HelpFormatter()
        
        helpFormatter.option_comparator = ReversedOptionComparator()

        out = StringIO()
        helpFormatter.print_usage(out, 80, app="app", options=options)

        assert out.getvalue() == f"usage: app [-c] [-b] [-a]{self.eol}"
    
    def test_print_sorted_usage_with_null_comparator(self):
        opts = Options()
        opts.add_option(Option("c", "first"))
        opts.add_option(Option("b", "second"))
        opts.add_option(Option("a", "third"))

        helpFormatter = HelpFormatter()
        helpFormatter.set_option_comparator(None)
        
        out = StringIO()
        helpFormatter.print_usage(out, 80, app="app", options=opts)
        assert out.getvalue() == f"usage: app [-c] [-b] [-a]{self.eol}"
    
    def test_print_usage(self):
        options = Options()
        options.add_option(Option.builder("a").desc("first").build())
        options.add_option(Option.builder("b").desc("second").build())
        options.add_option(Option.builder("c").desc("third").build())

        helpFormatter = HelpFormatter()
        out = StringIO()
        helpFormatter.print_usage(out, 80, app="app", options=options)

        assert out.getvalue() == f"usage: app [-a] [-b] [-c]{self.eol}"
    
    def test_render_wrapped_text_multi_line(self):
        # Multi line text
        width = 16
        padding = 0
        expected =  "aaaa aaaa aaaa" + self.eol + \
                    "aaaaaa" + self.eol + \
                    "aaaaa"
        
        sb = []
        HelpFormatter().render_wrapped_text(sb, width, padding, expected)
        
        assert expected == ''.join(sb), "multi line text"
    
    def test_render_wrapped_text_multi_line_padded(self):
        # Multi-line padded text
        width = 16
        padding = 4
        text =  "aaaa aaaa aaaa" + self.eol +\
                "aaaaaa" + self.eol + \
                "aaaaa"
        
        expected =  "aaaa aaaa aaaa" + self.eol + \
                    "    aaaaaa" + self.eol + \
                    "    aaaaa"
        
        sb = []
        HelpFormatter().render_wrapped_text(sb, width, padding, text)
        
        assert expected == ''.join(sb), "multi-line padded text"
    
    def test_render_wrapped_text_single_line(self):
        # Single line text
        width = 12
        padding = 0
        text = "This is a test."
        expected = "This is a" + self.eol + "test."

        sb = []
        HelpFormatter().render_wrapped_text(sb, width, padding, text)

        assert expected == ''.join(sb), "single line text"
    
    def test_render_wrapped_text_single_line_padded(self):
        # Single line padded text
        width = 12
        padding = 4
        text = "This is a test."
        expected = "This is a" + self.eol + "    test."

        sb = []
        HelpFormatter().render_wrapped_text(sb, width, padding, text)

        assert expected == ''.join(sb), "single line padded text"
    
    def test_render_wrapped_text_single_line_padded2(self):
        # Single line padded text 2
        width = 53
        padding = 24
        text =      "  -p,--period <PERIOD>  PERIOD is time duration of form " +\
                    "DATE[-DATE] where DATE has form YYYY[MM[DD]]"
        
        expected =  "  -p,--period <PERIOD>  PERIOD is time duration of" + self.eol +\
                    "                        form DATE[-DATE] where DATE" + self.eol +\
                    "                        has form YYYY[MM[DD]]"

        sb = []
        HelpFormatter().render_wrapped_text(sb, width, padding, text)

        assert expected == ''.join(sb), "single line padded text 2"
    
    def test_render_wrapped_text_word_cut(self):
        width = 7
        padding = 0
        text = "Thisisatest."
        expected = "Thisisa" + self.eol + "test."

        sb = []
        HelpFormatter().render_wrapped_text(sb, width, padding, text)

        assert expected == ''.join(sb), "cut and wrap"
    
    def test_rtrim(self):
        formatter = HelpFormatter()
        
        assert formatter.rtrim(None) == None
        assert formatter.rtrim("") == ""
        assert formatter.rtrim("   foo   ") == "   foo"
    
    def test_usage_with_long_opt_separator(self):
        options = Options()
        options.add_option("f", True, "the file")
        options.add_option(Option.builder('s').long_opt('size').desc('the size').has_arg().arg_name('SIZE').build())
        options.add_option(Option.builder().long_opt('age').desc('the age').has_arg().build())

        formatter = HelpFormatter()
        formatter.set_long_opt_separator("=")

        out = StringIO()
        
        formatter.print_usage(out, width=80, app='create', options=options)

        assert out.getvalue().strip() == 'usage: create [--age=<arg>] [-f <arg>] [-s <SIZE>]'
