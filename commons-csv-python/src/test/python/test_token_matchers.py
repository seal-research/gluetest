import pytest
from test.python.token_matchers import TokenMatchers
from main.python.token import Token


class TestTokenMatchers:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.token = Token()
        self.token.set_type(Token.Type.TOKEN)
        self.token.set_ready(True)
        self.token.append("content")

    def test_has_type(self):
        assert not (
            TokenMatchers.has_type(
                Token.Type.COMMENT)
            .matches(self.token)
        )
        assert not (
            TokenMatchers.has_type(
                Token.Type.EOF)
            .matches(self.token)
        )
        assert not (
            TokenMatchers.has_type(
                Token.Type.EORECORD)
            .matches(self.token)
        )
        assert (
            TokenMatchers.has_type(
                Token.Type.TOKEN)
            .matches(self.token)
        )

    def test_has_content(self):
        assert not (
            TokenMatchers.has_content(
                "This is not the token's content")
            .matches(self.token)
        )
        assert (
            TokenMatchers.has_content(
                "content")
            .matches(self.token)
        )

    def test_is_ready(self):
        assert (
            TokenMatchers.is_ready()
            .matches(self.token)
        )
        self.token.is_ready = False
        assert not (
            TokenMatchers.is_ready()
            .matches(self.token)
        )

    def test_matches(self):
        assert (
            TokenMatchers.matches(
                Token.Type.TOKEN, "content")
            .matches(self.token)
        )
        assert not (
            TokenMatchers.matches(
                Token.Type.EOF, "content")
            .matches(self.token)
        )
        assert not (
            TokenMatchers.matches(
                Token.Type.TOKEN, "not the content")
            .matches(self.token)
        )
        assert not (
            TokenMatchers.matches(
                Token.Type.EORECORD, "not the content")
            .matches(self.token)
        )
