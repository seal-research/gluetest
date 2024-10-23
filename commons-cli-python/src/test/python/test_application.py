import pytest
import os
import io
from main.python.gnu_parser import GnuParser
from main.python.options import Options
from main.python.posix_parser import PosixParser
from main.python.option import Option
from main.python.option_builder import OptionBuilder
from main.python.help_formatter import HelpFormatter


class TestApplication:
    """
    This is a collection of tests that test real world applications command lines.

    The following applications are tested:
    - ls
    - Ant
    - Groovy
    - man
    """

    def test_ant(self):
        """
        Ant test
        """
        # use the GNU parser
        parser = GnuParser()
        options = Options()
        options.add_option("help", False, "print this message")
        options.add_option("projecthelp", False, "print project help information")
        options.add_option("version", False, "print the version information and exit")
        options.add_option("quiet", False, "be extra quiet")
        options.add_option("verbose", False, "be extra verbose")
        options.add_option("debug", False, "print debug information")
        options.add_option("logfile", True, "use given file for log")
        options.add_option("logger", True, "the class which is to perform the logging")
        options.add_option(
            "listener", True, "add an instance of a class as a project listener"
        )
        options.add_option("buildfile", True, "use given buildfile")

        options.add_option(
            OptionBuilder()
            .with_description("use value for given property")
            .has_args()
            .with_value_separator()
            .create("D")
        )
        options.add_option(
            "find",
            True,
            "search for buildfile towards the root of the filesystem and use it",
        )

        args = [
            "-buildfile",
            "mybuild.xml",
            "-Dproperty=value",
            "-Dproperty1=value1",
            "-projecthelp",
        ]

        line = parser.parse(options, args)

        # check multiple values
        opts = line.get_option_values("D")
        assert "property" == opts[0]
        assert "value" == opts[1]
        assert "property1" == opts[2]
        assert "value1" == opts[3]

        # check single value
        assert line.get_option_value("buildfile") == "mybuild.xml"

        # check option
        assert line.has_option("projecthelp")

    def test_groovy(self):
        options = Options()

        options.add_option(
            OptionBuilder()
            .with_long_opt("define")
            .with_description("define a system property")
            .has_arg(True)
            .with_arg_name("name=value")
            .create("D")
        )
        options.add_option(
            OptionBuilder()
            .has_arg(False)
            .with_description("usage information")
            .with_long_opt("help")
            .create("h")
        )
        options.add_option(
            OptionBuilder()
            .has_arg(False)
            .with_description("debug mode will print out full stack traces")
            .with_long_opt("debug")
            .create("d")
        )
        options.add_option(
            OptionBuilder()
            .has_arg(False)
            .with_description("display the Groovy and JVM versions")
            .with_long_opt("version")
            .create("v")
        )
        options.add_option(
            OptionBuilder()
            .with_arg_name("charset")
            .has_arg()
            .with_description("specify the encoding of the files")
            .with_long_opt("encoding")
            .create("c")
        )
        options.add_option(
            OptionBuilder()
            .with_arg_name("script")
            .has_arg()
            .with_description("specify a command line script")
            .create("e")
        )
        options.add_option(
            OptionBuilder()
            .with_arg_name("extension")
            .has_optional_arg()
            .with_description(
                "modify files in place create backup if extension is given (e.g. '.bak')"
            )
            .create("i")
        )
        options.add_option(
            OptionBuilder()
            .has_arg(False)
            .with_description(
                "process files line by line using implicit 'line' variable"
            )
            .create("n")
        )
        options.add_option(
            OptionBuilder()
            .has_arg(False)
            .with_description(
                "process files line by line and print result (see also -n)"
            )
            .create("p")
        )
        options.add_option(
            OptionBuilder()
            .with_arg_name("port")
            .has_optional_arg()
            .with_description("listen on a port and process inbound lines")
            .create("l")
        )
        options.add_option(
            OptionBuilder()
            .with_arg_name("splitPattern")
            .has_optional_arg()
            .with_description(
                "split lines using splitPattern (default '\\s') using implicit 'split' variable"
            )
            .with_long_opt("autosplit")
            .create("a")
        )

        parser = PosixParser()
        line = parser.parse(options, ["-e", "println 'hello'"], True)

        assert line.has_option("e")
        assert "println 'hello'" == line.get_option_value("e")

    def test_ls(self):
        # create the command line parser
        parser = PosixParser()
        options = Options()
        options.add_option("a", "all", False, "do not hide entries starting with .")
        options.add_option("A", "almost-all", False, "do not list implied . and ..")
        options.add_option(
            "b", "escape", False, "print octal escapes for nongraphic characters"
        )
        options.add_option(
            OptionBuilder()
            .with_long_opt("block-size")
            .with_description("use SIZE-byte blocks")
            .has_arg()
            .with_arg_name("SIZE")
            .create()
        )
        options.add_option(
            "B", "ignore-backups", False, "do not list implied entried ending with ~"
        )
        options.add_option(
            "c",
            False,
            "with -lt: sort by, and show, ctime (time of last modification of file status information) with " +
            "-l:show ctime and sort by name otherwise: sort by ctime",
        )
        options.add_option("C", False, "list entries by columns")

        args = {"--block-size=10"}

        line = parser.parse(options, args)
        assert line.has_option("block-size")
        assert line.get_option_value("block-size") == "10"

    def test_man(self):
        cmd_line = (
            "man [-c|-f|-k|-w|-tZT device] [-adlhu7V] [-Mpath] [-Ppager] [-Slist] [-msystem] [-pstring] [-Llocale] [-eextension] [section]" +
            " page ..."
        )
        options = Options()
        options.add_option("a", "all", False, "find all matching manual pages.")
        options.add_option("d", "debug", False, "emit debugging messages.")
        options.add_option(
            "e", "extension", False, "limit search to extension type 'extension'."
        )
        options.add_option("f", "whatis", False, "equivalent to whatis.")
        options.add_option("k", "apropos", False, "equivalent to apropos.")
        options.add_option("w", "location", False, "print physical location of man page(s).")
        options.add_option("l", "local-file", False, "interpret 'page' argument(s) as local filename(s)")
        options.add_option("u", "update", False, "force a cache consistency check.")
        # FIXME - should generate -r,--prompt string
        options.add_option("r", "prompt", True, "provide 'less' pager with prompt.")
        options.add_option("c", "catman", False, "used by catman to reformat out of date cat pages.")
        options.add_option("7", "ascii", False, "display ASCII translation or certain latin1 chars.")
        options.add_option("t", "troff", False, "use troff format pages.")
        # FIXME - should generate -T,--troff-device device
        options.add_option("T", "troff-device", True, "use groff with selected device.")
        options.add_option("Z", "ditroff", False, "use groff with selected device.")
        options.add_option("D", "default", False, "reset all options to their default values.")
        # FIXME - should generate -M,--manpath path
        options.add_option(
            "M", "manpath", True, "set search path for manual pages to 'path'."
        )
        # FIXME - should generate -P,--pager pager
        options.add_option("P", "pager", True, "use program 'pager' to display output.")
        # FIXME - should generate -S,--sections list
        options.add_option("S", "sections", True, "use colon separated section list.")
        # FIXME - should generate -m,--systems system
        options.add_option("m", "systems", True, "search for man pages from other unix system(s).")
        # FIXME - should generate -L,--locale locale
        options.add_option("L", "locale", True, "define the locale for this particular man search.")
        # FIXME - should generate -p,--preprocessor string
        options.add_option(
            "p",
            "preprocessor",
            True,
            "string indicates which preprocessor to run.\n" +
            " e - [n]eqn  p - pic     t - tbl\n" +
            " g - grap    r - refer   v - vgrind",
        )
        options.add_option("V", "version", False, "show version.")
        options.add_option("h", "help", False, "show this usage message.")

        hf = HelpFormatter()
        eol = os.linesep
        pw = io.StringIO()
        hf.print_help(cmd_line, options, pw, 60, None, HelpFormatter.DEFAULT_LEFT_PAD, HelpFormatter.DEFAULT_DESC_PAD, None, False)
        out = pw.getvalue()
        inp = (
            "usage: man [-c|-f|-k|-w|-tZT device] [-adlhu7V] [-Mpath]" + eol +
            "           [-Ppager] [-Slist] [-msystem] [-pstring]" + eol +
            "           [-Llocale] [-eextension] [section] page ..." + eol +
            " -7,--ascii                display ASCII translation or" + eol +
            "                           certain latin1 chars." + eol +
            " -a,--all                  find all matching manual pages." + eol +
            " -c,--catman               used by catman to reformat out of" + eol +
            "                           date cat pages." + eol +
            " -d,--debug                emit debugging messages." + eol +
            " -D,--default              reset all options to their" + eol +
            "                           default values." + eol +
            " -e,--extension            limit search to extension type" + eol +
            "                           'extension'." + eol +
            " -f,--whatis               equivalent to whatis." + eol +
            " -h,--help                 show this usage message." + eol +
            " -k,--apropos              equivalent to apropos." + eol +
            " -l,--local-file           interpret 'page' argument(s) as" + eol +
            "                           local filename(s)" + eol +
            " -L,--locale <arg>         define the locale for this" + eol +
            "                           particular man search." + eol +
            " -M,--manpath <arg>        set search path for manual pages" + eol +
            "                           to 'path'." + eol +
            " -m,--systems <arg>        search for man pages from other" + eol +
            "                           unix system(s)." + eol +
            " -P,--pager <arg>          use program 'pager' to display" + eol +
            "                           output." + eol +
            " -p,--preprocessor <arg>   string indicates which" + eol +
            "                           preprocessor to run." + eol +
            "                           e - [n]eqn  p - pic     t - tbl" + eol +
            "                           g - grap    r - refer   v -" + eol +
            "                           vgrind" + eol +
            " -r,--prompt <arg>         provide 'less' pager with prompt." + eol +
            " -S,--sections <arg>       use colon separated section list." + eol +
            " -t,--troff                use troff format pages." + eol +
            " -T,--troff-device <arg>   use groff with selected device." + eol +
            " -u,--update               force a cache consistency check." + eol +
            " -V,--version              show version." + eol +
            " -w,--location             print physical location of man" + eol +
            "                           page(s)." + eol +
            " -Z,--ditroff              use groff with selected device." + eol
        )

        assert inp == out
    
    # Real world test with long and short options.
    def test_nlt(self):
        help = Option("h", "help", False, "print this message")
        version = Option("v", "version", False, "print version information")
        new_run = Option(
            "n", "new", False, "Create NLT cache entries only for new items"
        )
        tracker_run = Option(
            "t", "tracker", False, "Create NLT cache entries only for tracker items"
        )

        time_limit = (
            OptionBuilder()
            .with_long_opt("limit")
            .has_arg()
            .with_value_separator()
            .with_description("Set time limit for execution, in minutes")
            .create("l")
        )

        age = (
            OptionBuilder()
            .with_long_opt("age")
            .has_arg()
            .with_value_separator()
            .with_description("Age (in days) of cache item before being recomputed")
            .create("a")
        )

        server = (
            OptionBuilder()
            .with_long_opt("server")
            .has_arg()
            .with_value_separator()
            .with_description("The NLT server address")
            .create("s")
        )

        num_results = (
            OptionBuilder()
            .with_long_opt("results")
            .has_arg()
            .with_value_separator()
            .with_description("Number of results per item")
            .create("r")
        )

        config_file = (
            OptionBuilder()
            .with_long_opt("file")
            .has_arg()
            .with_value_separator()
            .with_description("Use the specified configuration file")
            .create()
        )

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

        # create the command line parser
        parser = PosixParser()

        args = ["-v", "-l", "10", "-age", "5", "-file", "filename"]

        line = parser.parse(options, args)

        assert line.has_option("v")
        assert line.get_option_value("l") == "10"
        assert line.get_option_value("limit") == "10"
        assert line.get_option_value("a") == "5"
        assert line.get_option_value("age") == "5"
        assert line.get_option_value("file") == "filename"
