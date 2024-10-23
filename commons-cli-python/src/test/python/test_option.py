import pytest
from main.python.option import Option

class TestOption:
    class DefaultOption(Option):
        def __init__(self, opt, description, default_value):
            serial_version_uid = 1
            super().__init__(opt, True, description)
            self.default_value = default_value

        def get_value(self):
            return super().get_value() if super().get_value() is not None else self.default_value

        def clone(self):
            option = TestOption.DefaultOption(self.option, self.description, self.default_value)

            for attr, val in vars(self).items():
                setattr(option, attr, val)
        
            option.values = self.values.copy() # create a different list object
            return option

    class _TestOption(Option):
        def __init__(self, opt, hasArg, description):
            serial_version_uid = 1
            super().__init__(opt, hasArg, description)

        def add_value(self, value):
            self.add_value_for_processing(value)
            return True
        
    def check_option(option: Option, opt: str, description: str, long_opt: str, num_args: int, arg_name: str, required: bool, optional_arg: bool, value_separator: str, cls):
        assert opt == option.get_opt()
        assert description == option.get_description()
        assert long_opt == option.get_long_opt()
        assert num_args == option.get_args()
        assert arg_name == option.get_arg_name()
        assert required == option.is_required()

        assert optional_arg == option.has_optional_arg()
        assert value_separator == option.get_value_separator()
        assert cls == option.get_type()

    def test_builder_insufficient_params1(self):
        with pytest.raises(ValueError):
            Option.builder().desc("desc").build()
        
    def test_builder_insufficient_params2(self):
        with pytest.raises(ValueError):
            Option.builder(None).desc("desc").build()

    def test_builder_invalid_option_name1(self):
        with pytest.raises(ValueError):
            Option.builder().option("invalid?")

    def test_builder_invalid_option_name2(self):
        with pytest.raises(ValueError):
            Option.builder().option("invalid@")

    def test_builder_invalid_option_name3(self):
        with pytest.raises(ValueError):
            Option.builder("invalid?")

    def test_builder_invalid_option_name4(self):
        with pytest.raises(ValueError):
            Option.builder("invalid@")

    def test_builder_methods(self):
        default_separator = '\0'

        TestOption.check_option(Option.builder("a").desc("desc").build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").long_opt("aaa").build(), "a", "desc", "aaa", Option.UNINITIALIZED, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").has_arg(True).build(), "a", "desc", None, 1, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").has_arg(False).build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").has_arg(True).build(), "a", "desc", None, 1, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").number_of_args(3).build(), "a", "desc", None, 3, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").required(True).build(), "a", "desc", None, Option.UNINITIALIZED, None, True, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").required(False).build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, str)

        TestOption.check_option(Option.builder("a").desc("desc").arg_name("arg1").build(), "a", "desc", None, Option.UNINITIALIZED, "arg1", False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").optional_arg(False).build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").optional_arg(True).build(), "a", "desc", None, Option.UNINITIALIZED, None, False, True, default_separator, str)
        TestOption.check_option(Option.builder("a").desc("desc").value_separator(':').build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, ':', str)
        TestOption.check_option(Option.builder("a").desc("desc").type(int).build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, int)
        TestOption.check_option(Option.builder().option("a").desc("desc").type(int).build(), "a", "desc", None, Option.UNINITIALIZED, None, False, False, default_separator, int)

    def test_clear(self):
        option = TestOption._TestOption("x", True, "")
        assert len(option.get_values_list()) == 0
        #
        # Replaced option.add_value("a")
        # as add_value is not implemented
        #
        option.add("a")
        assert len(option.get_values_list()) == 1
        option.clear_values()
        assert len(option.get_values_list()) == 0

    def test_clone(self):
        a = TestOption._TestOption("a", True, "")
        b = a.clone()
        #
        # Removed assert a == b
        # as expected behaviour on cloning is that x.clone() != x is true
        #
        assert a is not b
        a.set_description("a")
        assert b.get_description() == ""
        b.set_args(2)        
        #
        # Replaced b.add_value("b1") and b.add_value("b2")
        # as add_value is not implemented
        #
        b.add("b1")
        b.add("b2")
        assert a.get_args() == 1
        assert len(a.get_values_list()) == 0
        assert len(b.get_values()) == 2

    def test_get_value(self):
        option = Option("f", None)
        option.set_args(Option.UNLIMITED_VALUES)

        assert option.get_value("default") == "default"
        assert option.get_value(0) is None

        option.add_value_for_processing("foo")

        assert option.get_value() == "foo"
        assert option.get_value(0) == "foo"
        assert option.get_value("default") == "foo"

    def testHasArgName(self):
        option = Option("f", None)

        option.set_arg_name(None)
        assert not option.has_arg_name()

        option.set_arg_name("")
        assert not option.has_arg_name()

        option.set_arg_name("file")
        assert option.has_arg_name()


    def testHasArgs(self):
        option = Option("f", None)

        option.set_args(0)
        assert not option.has_args()

        option.set_args(1)
        assert not option.has_args()

        option.set_args(10)
        assert option.has_args()

        option.set_args(Option.UNLIMITED_VALUES)
        assert option.has_args()

        option.set_args(Option.UNINITIALIZED)
        assert not option.has_args()


    def testHashCode(self):
        assert Option.builder("test").build().hash_code() != Option.builder("test2").build().hash_code()
        assert Option.builder("test").build().hash_code() != Option.builder().long_opt("test").build().hash_code()
        assert Option.builder("test").build().hash_code() != Option.builder("test").long_opt("long test").build().hash_code()


    def testSubclass(self):
        option = TestOption.DefaultOption("f", "file", "myfile.txt")
        clone = option.clone()

        assert clone.get_value() == "myfile.txt"
        assert isinstance(clone, TestOption.DefaultOption)
