import pytest
from parser_test_case import ParserTestCase
from main.python.basic_parser import BasicParser

class TestBasicParser(ParserTestCase):
    @pytest.fixture(autouse=True)
    def set_up(self):
        self._set_up()
        self.parser = BasicParser()

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_ambiguous_long_without_equal_single_dash(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_ambiguous_partial_long_option1(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_ambiguous_partial_long_option2(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_ambiguous_partial_long_option3(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_ambiguous_partial_long_option4(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_bursting(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_double_dash2(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_long_option_with_equals_quote_handling(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_long_with_equal_double_dash(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_long_with_equal_single_dash(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_long_without_equal_single_dash(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_missing_arg_with_bursting(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser (CLI-184)")
    def test_negative_option(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_partial_long_option_single_dash(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_properties_option1(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_properties_option2(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_short_option_concatenated_quote_handling(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_short_with_equal(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_short_without_equal(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_stop_bursting(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_stop_bursting2(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_unambiguous_partial_long_option1(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_unambiguous_partial_long_option2(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_unambiguous_partial_long_option3(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_unambiguous_partial_long_option4(self):
        pass

    @pytest.mark.skip(reason="Not supported by the BasicParser")
    def test_unrecognized_option_with_bursting(self):
        pass
