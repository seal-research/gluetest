import pytest
import os
from io import StringIO
from main.python.help_formatter import HelpFormatter
from main.python.options import Options
from main.python.option import Option
from main.python.option_group import OptionGroup

class TestBugsCLI162:

    @pytest.fixture(autouse=True)
    def set_up(self):
        # Constant for the line separator.
        self.CR = os.linesep

        # Constants used for options
        self.OPT = "-"
        self.OPT_COLUMN_NAMES = "l"
        self.OPT_CONNECTION = "c"
        self.OPT_DESCRIPTION = "e"
        self.OPT_DRIVER = "d"
        self.OPT_DRIVER_INFO = "n"
        self.OPT_FILE_BINDING = "b"
        self.OPT_FILE_JDBC = "j"
        self.OPT_FILE_SFMD = "f"
        self.OPT_HELP = "h"
        self.OPT_HELP_LONG = "help"
        self.OPT_INTERACTIVE = "i"
        self.OPT_JDBC_TO_SFMD = "2"
        self.OPT_JDBC_TO_SFMD_L = "jdbc2sfmd"
        self.OPT_METADATA = "m"
        self.OPT_PARAM_MODES_INT = "o"
        self.OPT_PARAM_MODES_NAME = "O"
        self.OPT_PARAM_NAMES = "a"
        self.OPT_PARAM_TYPES_INT = "y"
        self.OPT_PARAM_TYPES_NAME = "Y"
        self.OPT_PASSWORD = "p"
        self.OPT_PASSWORD_L = "password"
        self.OPT_SQL = "s"
        self.OPT_SQL_L = "sql"
        self.OPT_STACK_TRACE = "t"
        self.OPT_TIMING = "g"
        self.OPT_TRIM_L = "trim"
        self.OPT_USER = "u"
        self.OPT_WRITE_TO_FILE = "w"
        self.PMODE_IN = "IN"
        self.PMODE_INOUT = "INOUT"
        self.PMODE_OUT = "OUT"
        self.PMODE_UNK = "Unknown"
        self.PMODES = self.PMODE_IN + ", " + self.PMODE_INOUT + ", " + self.PMODE_OUT + ", " + self.PMODE_UNK

        self.formatter = HelpFormatter()
        self.sw = StringIO()

    def test_infinite_loop(self):
        options = Options()
        options.add_option("h", "help", False, "This is a looooong description")
        # used to hang & crash
        self.formatter.print_help(pw=self.sw, width=20, cmd_line_syntax="app", header=None, options=options, left_pad=HelpFormatter.DEFAULT_LEFT_PAD, desc_pad=HelpFormatter.DEFAULT_DESC_PAD, footer=None)

        expected = "usage: app" + self.CR + \
                " -h,--help   This is" + self.CR + \
                "             a" + self.CR + \
                "             looooon" + self.CR + \
                "             g" + self.CR + \
                "             descrip" + self.CR + \
                "             tion" + self.CR
        assert self.sw.getvalue() == expected

    def test_long_line_chunking(self):
        options = Options()
        options.add_option("x", "extralongarg", False,
                          "This description has ReallyLongValuesThatAreLongerThanTheWidthOfTheColumns " +
                          "and also other ReallyLongValuesThatAreHugerAndBiggerThanTheWidthOfTheColumnsBob, " +
                          "yes. ")
        self.formatter.print_help(pw=self.sw, width=35, cmd_line_syntax=self.__class__.__name__, header="Header", options=options, left_pad=0, desc_pad=5, footer="Footer")
        expected = "usage: TestBugsCLI162" + self.CR + \
                          "Header" + self.CR + \
                          "-x,--extralongarg     This" + self.CR + \
                          "                      description" + self.CR + \
                          "                      has" + self.CR + \
                          "                      ReallyLongVal" + self.CR + \
                          "                      uesThatAreLon" + self.CR + \
                          "                      gerThanTheWid" + self.CR + \
                          "                      thOfTheColumn" + self.CR + \
                          "                      s and also" + self.CR + \
                          "                      other" + self.CR + \
                          "                      ReallyLongVal" + self.CR + \
                          "                      uesThatAreHug" + self.CR + \
                          "                      erAndBiggerTh" + self.CR + \
                          "                      anTheWidthOfT" + self.CR + \
                          "                      heColumnsBob," + self.CR + \
                          "                      yes." + self.CR + \
                          "Footer" + self.CR 

        assert self.sw.getvalue() == expected, "Long arguments did not split as expected"

    def test_long_line_chunking_indent_ignored(self):
        options = Options()
        options.add_option("x", "extralongarg", False, "This description is Long.")
        self.formatter.print_help(pw=self.sw, width=22, cmd_line_syntax=self.__class__.__name__, header="Header", options=options, left_pad=0, desc_pad=5, footer="Footer")
        expected = "usage: TestBugsCLI162" + self.CR + \
                          "Header" + self.CR + \
                          "-x,--extralongarg" + self.CR + \
                          " This description is" + self.CR + \
                          " Long." + self.CR + \
                          "Footer" + self.CR
        assert self.sw.getvalue() == expected, "Long arguments did not split as expected"

    def test_print_help_long_lines(self):
        # Options build
        command_line_options = Options()
        command_line_options.add_option(self.OPT_HELP, self.OPT_HELP_LONG, False, "Prints help and quits")
        command_line_options.add_option(self.OPT_DRIVER, "driver", True, "JDBC driver class name")
        command_line_options.add_option(self.OPT_DRIVER_INFO, "info", False, "Prints driver information and properties. If "
            + self.OPT
            + self.OPT_CONNECTION
            + " is not specified, all drivers on the classpath are displayed.")
        command_line_options.add_option(self.OPT_CONNECTION, "url", True, "Connection URL")
        command_line_options.add_option(self.OPT_USER, "user", True, "A database user name")
        command_line_options.add_option(self.OPT_PASSWORD, self.OPT_PASSWORD_L, True,
            "The database password for the user specified with the "
            + self.OPT
            + self.OPT_USER
            + " option. You can obfuscate the password with org.mortbay.jetty.security.Password,"
            + " see http://docs.codehaus.org/display/JETTY/Securing+Passwords")
        
        command_line_options.add_option(self.OPT_SQL, self.OPT_SQL_L, True, "Runs SQL or {call stored_procedure(?, ?)} or {?=call function(?, ?)}")
        command_line_options.add_option(self.OPT_FILE_SFMD, "sfmd", True, "Writes a SFMD file for the given SQL")
        command_line_options.add_option(self.OPT_FILE_BINDING, "jdbc", True, "Writes a JDBC binding node file for the given SQL")
        command_line_options.add_option(self.OPT_FILE_JDBC, "node", True, "Writes a JDBC node file for the given SQL (internal debugging)")
        command_line_options.add_option(self.OPT_WRITE_TO_FILE, "outfile", True, "Writes the SQL output to the given file")
        command_line_options.add_option(self.OPT_DESCRIPTION, "description", True,
            "SFMD description. A default description is used if omited. Example: " + self.OPT + self.OPT_DESCRIPTION + " \"Runs such and such\"")
        command_line_options.add_option(self.OPT_INTERACTIVE, "interactive", False,
            "Runs in interactive mode, reading and writing from the console, 'go' or '/' sends a statement")
        command_line_options.add_option(self.OPT_TIMING, "printTiming", False, "Prints timing information")
        command_line_options.add_option(self.OPT_METADATA, "printMetaData", False, "Prints metadata information")
        command_line_options.add_option(self.OPT_STACK_TRACE, "printStack", False, "Prints stack traces on errors")
        option = Option(self.OPT_COLUMN_NAMES, "columnNames", True, "Column XML names; default names column labels. Example: "
            + self.OPT
            + self.OPT_COLUMN_NAMES
            + " \"cname1 cname2\"")
        command_line_options.add_option(option)
        
        option = Option(self.OPT_PARAM_NAMES, "paramNames", True, "Parameter XML names; default names are param1, param2, etc. Example: "
                        + self.OPT
                        + self.OPT_PARAM_NAMES
                        + " \"pname1 pname2\"")
        command_line_options.add_option(option)

        p_out_types_option_group = OptionGroup()
        p_out_types_option_group_doc = self.OPT + self.OPT_PARAM_TYPES_INT + " and " + self.OPT + self.OPT_PARAM_TYPES_NAME + " are mutually exclusive."
        types_class_name = "type"

        option = Option(self.OPT_PARAM_TYPES_INT, "paramTypes", True, "Parameter types from "
            + types_class_name
            + ". "
            + p_out_types_option_group_doc
            + " Example: "
            + self.OPT
            + self.OPT_PARAM_TYPES_INT
            + " \"-10 12\"")
        command_line_options.add_option(option)
        
        option = Option(self.OPT_PARAM_TYPES_NAME, "paramTypeNames", True, "Parameter "
                        + types_class_name
                        + " names. "
                        + p_out_types_option_group_doc
                        + " Example: "
                        + self.OPT
                        + self.OPT_PARAM_TYPES_NAME
                        + " \"CURSOR VARCHAR\"")
        command_line_options.add_option(option)
        command_line_options.add_option_group(p_out_types_option_group)

        modes_option_group = OptionGroup()
        modes_option_group_doc = self.OPT + self.OPT_PARAM_MODES_INT + " and " + self.OPT + self.OPT_PARAM_MODES_NAME + " are mutually exclusive."

        option = Option(self.OPT_PARAM_MODES_INT, "paramModes", True, "Parameters modes ("
                        + str(1) # parameter mode in
                        + "=IN, "
                        + str(2) # parameter mode inout
                        + "=INOUT, "
                        + str(4) # parameter mode out
                        + "=OUT, "
                        + str(0) # parameter mode unknown
                        + "=Unknown"
                        + "). "
                        + modes_option_group_doc
                        + " Example for 2 parameters, OUT and IN: "
                        + self.OPT
                        + self.OPT_PARAM_MODES_INT
                        + " \""
                        + str(4) # parameter mode out
                        + " "
                        + str(1) # parameter mode in
                        + "\"")
        
        modes_option_group.add_option(option)
        
        option = Option(self.OPT_PARAM_MODES_NAME, "paramModeNames", True, "Parameters mode names ("
                        + self.PMODES
                        + "). "
                        + modes_option_group_doc
                        + " Example for 2 parameters, OUT and IN: "
                        + self.OPT
                        + self.OPT_PARAM_MODES_NAME
                        + " \""
                        + self.PMODE_OUT
                        + " "
                        + self.PMODE_IN
                        + "\"")
        modes_option_group.add_option(option)
        command_line_options.add_option_group(modes_option_group)

        option = Option(None, self.OPT_TRIM_L, True,
            "Trims leading and trailing spaces from all column values. Column XML names can be optionally specified to set which columns to trim.")
        option.set_optional_arg(True)
        command_line_options.add_option(option)

        option = Option(self.OPT_JDBC_TO_SFMD, self.OPT_JDBC_TO_SFMD_L, True,
            "Converts the JDBC file in the first argument to an SMFD file specified in the second argument.")
        option.set_args(2)
        command_line_options.add_option(option)

        self.formatter.print_help(pw=self.sw, width=HelpFormatter.DEFAULT_WIDTH, cmd_line_syntax=self.__class__.__name__, header=None, options=command_line_options,
            left_pad=HelpFormatter.DEFAULT_LEFT_PAD, desc_pad=HelpFormatter.DEFAULT_DESC_PAD, footer=None)
        
        expected = "usage: TestBugsCLI162" + self.CR + \
                " -2,--jdbc2sfmd <arg>        Converts the JDBC file in the first argument" + self.CR + \
                "                             to an SMFD file specified in the second" + self.CR + \
                "                             argument." + self.CR + \
                " -a,--paramNames <arg>       Parameter XML names; default names are" + self.CR + \
                "                             param1, param2, etc. Example: -a \"pname1" + self.CR + \
                "                             pname2\"" + self.CR + \
                " -b,--jdbc <arg>             Writes a JDBC binding node file for the given" + self.CR + \
                "                             SQL" + self.CR + \
                " -c,--url <arg>              Connection URL" + self.CR + \
                " -d,--driver <arg>           JDBC driver class name" + self.CR + \
                " -e,--description <arg>      SFMD description. A default description is" + self.CR + \
                "                             used if omited. Example: -e \"Runs such and" + self.CR + \
                "                             such\"" + self.CR + \
                " -f,--sfmd <arg>             Writes a SFMD file for the given SQL" + self.CR + \
                " -g,--printTiming            Prints timing information" + self.CR + \
                " -h,--help                   Prints help and quits" + self.CR + \
                " -i,--interactive            Runs in interactive mode, reading and writing" + self.CR + \
                "                             from the console, 'go' or '/' sends a" + self.CR + \
                "                             statement" + self.CR + \
                " -j,--node <arg>             Writes a JDBC node file for the given SQL" + self.CR + \
                "                             (internal debugging)" + self.CR + \
                " -l,--columnNames <arg>      Column XML names; default names column" + self.CR + \
                "                             labels. Example: -l \"cname1 cname2\"" + self.CR + \
                " -m,--printMetaData          Prints metadata information" + self.CR + \
                " -n,--info                   Prints driver information and properties. If" + self.CR + \
                "                             -c is not specified, all drivers on the" + self.CR + \
                "                             classpath are displayed." + self.CR + \
                " -o,--paramModes <arg>       Parameters modes (1=IN, 2=INOUT, 4=OUT," + self.CR + \
                "                             0=Unknown). -o and -O are mutually exclusive." + self.CR + \
                "                             Example for 2 parameters, OUT and IN: -o \"4" + self.CR + \
                "                             1\"" + self.CR + \
                " -O,--paramModeNames <arg>   Parameters mode names (IN, INOUT, OUT," + self.CR + \
                "                             Unknown). -o and -O are mutually exclusive." + self.CR + \
                "                             Example for 2 parameters, OUT and IN: -O \"OUT" + self.CR + \
                "                             IN\"" + self.CR + \
                " -p,--password <arg>         The database password for the user specified" + self.CR + \
                "                             with the -u option. You can obfuscate the" + self.CR + \
                "                             password with" + self.CR + \
                "                             org.mortbay.jetty.security.Password, see" + self.CR + \
                "                             http://docs.codehaus.org/display/JETTY/Securi" + self.CR + \
                "                             ng+Passwords" + self.CR + \
                " -s,--sql <arg>              Runs SQL or {call stored_procedure(?, ?)} or" + self.CR + \
                "                             {?=call function(?, ?)}" + self.CR + \
                " -t,--printStack             Prints stack traces on errors" + self.CR + \
                "    --trim <arg>             Trims leading and trailing spaces from all" + self.CR + \
                "                             column values. Column XML names can be" + self.CR + \
                "                             optionally specified to set which columns to" + self.CR + \
                "                             trim." + self.CR + \
                " -u,--user <arg>             A database user name" + self.CR + \
                " -w,--outfile <arg>          Writes the SQL output to the given file" + self.CR + \
                " -y,--paramTypes <arg>       Parameter types from type. -y and -Y are" + self.CR + \
                "                             mutually exclusive. Example: -y \"-10 12\"" + self.CR + \
                " -Y,--paramTypeNames <arg>   Parameter type names. -y and -Y are mutually" + self.CR + \
                "                             exclusive. Example: -Y \"CURSOR VARCHAR\"" + self.CR 
        assert self.sw.getvalue() == expected
