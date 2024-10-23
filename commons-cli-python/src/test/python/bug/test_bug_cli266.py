import pytest
from main.python.options import Options
from main.python.option_group import OptionGroup
from main.python.option import Option
from main.python.help_formatter import HelpFormatter

class TestBugCLI266:
    inserted_order = ["h", "d", "f", "x", "s", "p", "t", "y", "w", "o"]
    sort_order = ["d", "f", "h", "o", "p", "s", "t", "w", "x"]

    def _build_options_group(self, options: Options):
        first_group = OptionGroup()
        second_group = OptionGroup()
        first_group.set_required(True)
        second_group.set_required(True)
        
        first_group.add_option(Option.builder("d")
                                .long_opt("db")
                                .has_arg()
                                .arg_name("table-name")
                                .build())
        first_group.add_option(Option.builder("f")
                               .long_opt("flat-file")
                               .has_arg()
                               .arg_name("input.csv")
                               .build())
        
        options.add_option_group(first_group)
        
        second_group.add_option(Option.builder("x")
                                .has_arg()
                                .arg_name("arg1")
                                .build())
        second_group.add_option(Option.builder("s").build())
        second_group.add_option(Option.builder("p")
                                .has_arg()
                                .arg_name("arg1")
                                .build())
        
        options.add_option_group(second_group)
    
    def _get_options(self) -> Options:
        options = Options()
        
        help = Option.builder("h") \
                .long_opt("help")  \
                .desc("Prints this help message") \
                .build()
        
        options.add_option(help)
        
        self._build_options_group(options)
        
        t = Option.builder("t") \
                    .required() \
                    .has_arg() \
                    .arg_name("file") \
                    .build()
        
        w = Option.builder("w") \
                    .required() \
                    .has_arg() \
                    .arg_name("word") \
                    .build()
        
        o = Option.builder("o") \
                    .has_arg() \
                    .arg_name("directory") \
                    .build()
        
        options.add_option(t)
        options.add_option(w)
        options.add_option(o)
        
        return options
    
    def test_option_comparator_default_order(self):
        formatter = HelpFormatter()
        options = self._get_options().get_options()

        options.sort(key=formatter.get_option_comparator().compare)
        
        i = 0
        o: Option
        for o in options:
            assert o.get_opt(), TestBugCLI266.sort_order[i]
            i += 1
    
    def test_option_comparator_inserted_order(self):
        options = self._get_options().get_options()
        
        i = 0
        o: Option
        for o in options:
            assert o.get_opt(), TestBugCLI266.inserted_order[i]
            i += 1
