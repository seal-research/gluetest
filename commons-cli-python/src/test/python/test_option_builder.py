import pytest
from main.python.option_builder import OptionBuilder

class TestOptionBuilder:

    def test_base_option_chat_opt(self):
        base = OptionBuilder.with_description("option description").create('o')

        assert "o" == base.get_opt()
        assert "option description" == base.get_description()
        assert not base.has_arg()

    def test_base_option_string_opt(self):
        base = OptionBuilder.with_description("option description").create("o")

        assert "o" == base.get_opt()
        assert "option description" == base.get_description()
        assert not base.has_arg()

    def test_builder_is_resetted_always(self):
        try:
            OptionBuilder.with_description("JUnit").create('"')
            pytest.fail("ValueError expected")
        except ValueError:
            pass
        assert OptionBuilder.create('x').get_description() is None, "we inherited a description"

        try:
            OptionBuilder.with_description("JUnit").create()
            pytest.fail("ValueError expected")
        except ValueError:
            pass
        assert OptionBuilder.create('x').get_description() is None, "we inherited a description"
    
    def test_complete_option(self):
        simple = OptionBuilder.with_long_opt("simple option") \
            .has_arg() \
            .is_required() \
            .has_args() \
            .with_type(float) \
            .with_description("this is a simple option") \
            .create('s')
        
        assert "s" == simple.get_opt()
        assert "simple option" == simple.get_long_opt()
        assert "this is a simple option" == simple.get_description()
        assert simple.get_type() == float
        assert simple.has_arg()
        assert simple.is_required()
        assert simple.has_args()

    def test_create_incomplete_option(self):
        try:
            OptionBuilder.has_arg().create()
            pytest.fail("Incomplete option should be rejected")
        except ValueError:
            OptionBuilder.create("opt")

    def test_illegal_options(self):
        # bad single character option
        try:
            OptionBuilder.with_description("option description").create('"')
            pytest.fail("ValueError not caught")
        except ValueError:
            pass

        # bad character in option string
        try:
            OptionBuilder.create("opt`")
            pytest.fail("ValueError not caught")
        except ValueError:
            pass

        # valid option
        try:
            OptionBuilder.create("opt")
            # success
        except ValueError:
            pytest.fail("ValueError caught")

    def test_option_arg_numbers(self):
        opt = OptionBuilder.with_description("option description") \
            .has_args(2) \
            .create('o')
        assert 2 == opt.get_args()

    def test_special_opt_chars(self):
        # '?'
        opt1 = OptionBuilder.with_description("help options").create('?')
        assert "?" == opt1.get_opt()

        # '@'
        opt2 = OptionBuilder.with_description("read from stdin").create('@')
        assert "@" == opt2.get_opt()

        # ' '
        try:
            OptionBuilder.create(' ')
            pytest.fail("ValueError not caught")
        except ValueError:
            pass

    def test_two_complete_options(self):
        simple = OptionBuilder.with_long_opt("simple option") \
            .has_arg() \
            .is_required() \
            .has_args() \
            .with_type(float) \
            .with_description("this is a simple option") \
            .create('s')
        
        assert "s" == simple.get_opt()
        assert "simple option" == simple.get_long_opt()
        assert "this is a simple option" == simple.get_description()
        assert simple.get_type() == float
        assert simple.has_arg()
        assert simple.is_required()
        assert simple.has_args()

        simple = OptionBuilder.with_long_opt("dimple option") \
            .has_arg() \
            .with_description("this is a dimple option") \
            .create('d')
        
        assert "d" == simple.get_opt()
        assert "dimple option" == simple.get_long_opt()
        assert "this is a dimple option" == simple.get_description()
        assert simple.get_type() == str
        assert simple.has_arg()
        assert not simple.is_required()
        assert not simple.has_args()
