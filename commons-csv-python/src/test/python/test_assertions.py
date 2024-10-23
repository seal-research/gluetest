import pytest
from main.python.assertions import Assertions


class TestAssertions:

    def test_not_null(self):
        Assertions.not_null(object(), "object")

    def test_not_null_null(self):
        with pytest.raises(ValueError):
            Assertions.not_null(None, "object")
