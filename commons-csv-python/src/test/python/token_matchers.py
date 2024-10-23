from main.python.token import Token
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest import all_of


class TokenMatchers:
    
    @staticmethod
    def has_type(expected_type: Token.Type):
        class HasType(BaseMatcher):
            def describe_to(self, description: Description):
                description.append_text("token has type ")
                description.append_list("", ", ", "", [expected_type])

            def _matches(self, item: Token, mismatch_description: Description | None = None):
                if mismatch_description:
                    mismatch_description.append_text("token type is ")
                    mismatch_description.append_list("", ", ", "", [item.type])
                return item.type == expected_type

        return HasType()

    @staticmethod
    def has_content(expected_content: str):
        class HasContent(BaseMatcher):
            def describe_to(self, description: Description):
                description.append_text("token has content ")
                description.append_list("", ", ", "", [expected_content])

            def _matches(self, item: Token, mismatch_description: Description | None = None):
                if mismatch_description:
                    mismatch_description.append_text("token content is ")
                    mismatch_description.append_list("", ", ", "", [str(item.content)])
                return str(item.content) == expected_content

        return HasContent()

    @staticmethod
    def is_ready():
        class IsReady(BaseMatcher):
            def describe_to(self, description: Description):
                description.append_text("token is ready ")

            def _matches(self, item: Token, mismatch_description: Description | None = None):
                if mismatch_description:
                    mismatch_description.append_text("token is not ready ")
                return item.is_ready

        return IsReady()

    @staticmethod
    def matches(expected_type: Token.Type, expected_content: str):
        type_matcher = TokenMatchers.has_type(expected_type)
        content_matcher = TokenMatchers.has_content(expected_content)
        return all_of(type_matcher, content_matcher)
