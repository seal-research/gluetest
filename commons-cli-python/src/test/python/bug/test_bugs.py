import io
import os
import sys
import pytest
from main.python.help_formatter import HelpFormatter
from main.python.options import Options
from main.python.option import Option
from main.python.option_group import OptionGroup
from main.python.option_builder import OptionBuilder
from main.python.posix_parser import PosixParser
from main.python.gnu_parser import GnuParser
from main.python.missing_argument_exception import MissingArgumentException
from main.python.parse_exception import ParseException

class TestBugs:

    def test_11456(self):
        # Posix
        options = Options()
        options.add_option(OptionBuilder.has_optional_arg().create('a'))
        options.add_option(OptionBuilder.has_arg().create('b'))
        args = ["-a", "-bvalue"]

        parser = PosixParser()

        cmd = parser.parse(options, args)
        assert cmd.get_option_value('b') == "value"

        # GNU
        options = Options()
        options.add_option(OptionBuilder.has_optional_arg().create('a'))
        options.add_option(OptionBuilder.has_arg().create('b'))   
        args = ["-a", "-b", "value"]

        parser = GnuParser()

        cmd = parser.parse(options, args)
        assert cmd.get_option_value('b') == "value"

    def test_11457(self):
        options = Options()
        options.add_option(OptionBuilder.with_long_opt("verbose").create())
        args = ["--verbose"]

        parser = PosixParser()

        cmd = parser.parse(options, args)
        assert cmd.has_option("verbose")
    
    def test_11458(self):
        options = Options()
        options.add_option(OptionBuilder.with_value_separator('=').has_args().create('D'))
        options.add_option(OptionBuilder.with_value_separator(':').has_args().create('p'))
        args = ["-DJAVA_HOME=/opt/java", "-pfile1:file2:file3"]

        parser = PosixParser()

        cmd = parser.parse(options, args)

        values = cmd.get_option_values('D')

        assert values[0] == "JAVA_HOME"
        assert values[1] == "/opt/java"

        values = cmd.get_option_values('p')

        assert values[0] == "file1"
        assert values[1] == "file2"
        assert values[2] == "file3"

        for opt in cmd.iterator():
            if opt.get_id() == 'D':
                assert opt.get_value(0) == "JAVA_HOME"
                assert opt.get_value(1) == "/opt/java"
            elif opt.get_id() == 'p':
                assert opt.get_value(0) == "file1"
                assert opt.get_value(1) == "file2"
                assert opt.get_value(2) == "file3"
            else:
                pytest.fail("-D option not found")

    def test_11680(self):
        options = Options()
        options.add_option("f", True, "foobar")
        options.add_option("m", True, "missing")
        args = ["-f", "foo"]

        parser = PosixParser()

        cmd = parser.parse(options, args)

        cmd.get_option_value("f", "default f")
        cmd.get_option_value("m", "default m")

    def test_12210(self):
        # create the main options object which will handle the first parameter
        main_options = Options()
        # There can be 2 main exclusive options: -exec|-rep

        # Therefore, place them in an option group

        argv = ["-exec", "-exec_opt1", "-exec_opt2"]
        grp = OptionGroup()

        grp.add_option(Option("exec", False, "description for this option"))

        grp.add_option(Option("rep", False, "description for this option"))

        main_options.add_option_group(grp)

        # for the exec option, there are 2 options...
        exec_options = Options()
        exec_options.add_option("exec_opt1", False, " desc")
        exec_options.add_option("exec_opt2", False, " desc")

        # similarly, for rep there are 2 options...
        rep_options = Options()
        rep_options.add_option("repopto", False, "desc")
        rep_options.add_option("repoptt", False, "desc")

        # create the parser
        parser = GnuParser()

        # finally, parse the arguments:

        # first parse the main options to see what the user has specified
        # We set stop_at_non_option to true so it does not touch the remaining
        # options
        cmd = parser.parse(main_options, argv, True)
        # get the remaining options...
        argv = cmd.get_args()

        if cmd.has_option("exec"):
            cmd = parser.parse(exec_options, argv, False)
            # process the exec_op1 and exec_opt2...
            assert cmd.has_option("exec_opt1")
            assert cmd.has_option("exec_opt2")
        elif cmd.has_option("rep"):
            cmd = parser.parse(rep_options, argv, False)
            # process the rep_op1 and rep_opt2...
        else:
            pytest.fail("exec option not found")

    def test_13425(self):
        options = Options()
        
        oldpass = OptionBuilder.with_long_opt("old-password") \
            .with_description("Use this option to specify the old password") \
            .has_arg() \
            .create('o')
        newpass = OptionBuilder.with_long_opt("new-password") \
            .with_description("Use this option to specify the new password") \
            .has_arg() \
            .create('n')
        
        args = ["-o", "-n", "newpassword"]

        options.add_option(oldpass)
        options.add_option(newpass)

        parser = PosixParser()

        try:
            parser.parse(options, args)
            pytest.fail("MissingArgumentException not caught.")
        except MissingArgumentException:
            pass

    def test_13666(self):
        options = Options()
        dir = OptionBuilder.with_description("dir").has_arg().create('d')
        options.add_option(dir)

        try:
            pw = io.StringIO()

            eol = os.linesep

            formatter = HelpFormatter()
            sys.stdout = pw
            formatter.print_help("dir", options, pw=sys.stdout)

            assert "usage: dir" + eol + " -d <arg>   dir" + eol == sys.stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__

    def test_13935(self):
        directions = OptionGroup()

        left = Option("l", "left", False, "go left")
        right = Option("r", "right", False, "go right")
        straight = Option("s", "straight", False, "go straight")
        forward = Option("f", "forward", False, "go forward")
        forward.set_required(True)

        directions.add_option(left)
        directions.add_option(right)
        directions.set_required(True)

        opts = Options()
        opts.add_option_group(directions)
        opts.add_option(straight)

        parser = PosixParser()

        args = []
        try:
            parser.parse(opts, args)
            pytest.fail("ParseException not caught.")
        except ParseException:
            pass
        
        args = ["-s", "-l"]
        line = parser.parse(opts, args)
        assert line is not None

        opts.add_option(forward)
        args = ["-s", "-l", "-f"]
        line = parser.parse(opts, args)
        assert line is not None

    def test_14786(self):
        o = OptionBuilder.is_required().with_description("test").create("test")
        opts = Options()
        opts.add_option(o)
        opts.add_option(o)

        parser = GnuParser()

        args = ["-test"]

        line = parser.parse(opts, args)
        assert line.has_option('test')

    def test_15046(self):
        parser = PosixParser()
        cli_args = ["-z", "c"]

        options = Options()
        options.add_option(Option("z", "timezone", True, "affected option"))

        parser.parse(options, cli_args)

        # now add conflicting option
        options.add_option("c", "conflict", True, "conflict option")
        line = parser.parse(options, cli_args)
        assert line.get_option_value('z') == "c"
        assert not line.has_option("c")

    def test_15648(self):
        parser = PosixParser()
        args = ["-m", "\"Two Words\""]
        m = OptionBuilder.has_args().create("m")
        options = Options()
        options.add_option(m)
        line = parser.parse(options, args)
        assert line.get_option_value("m") == "Two Words"
    
    def test_31148(self):
        multi_arg_option = Option("o", "option with multiple args")
        multi_arg_option.set_args(1)

        options = Options()
        options.add_option(multi_arg_option)

        parser = PosixParser()
        args = []
        props = {}
        props["o"] = "ovalue"
        cl = parser.parse(options, args, props)

        assert cl.has_option('o')
        assert cl.get_option_value('o') == "ovalue"
