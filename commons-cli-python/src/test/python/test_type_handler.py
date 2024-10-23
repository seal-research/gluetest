import pytest
from main.python.type_handler import TypeHandler
from main.python.pattern_option_builder import PatternOptionBuilder
from main.python.parse_exception import ParseException
import os
import urllib

class Instantiable:
    pass

class NotInstantiable:
    def __init__(self):
        raise TypeError("This class is not instantiable") 
        # This was not implemented in the original Java code, but is needed here to prevent the class from being instantiated
        # Original code may have a bug here

class TestTypeHandler:

    @pytest.fixture(autouse=True)
    def set_up(self):
        TypeHandler.update_namespace_classes(self, globals())

    def test_create_value_class(self):
        clazz = TypeHandler.create_value(Instantiable.__name__, PatternOptionBuilder.CLASS_VALUE)
        assert clazz == Instantiable

    def test_create_value_class_not_found(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value("what ever", PatternOptionBuilder.CLASS_VALUE)

    def test_create_value_date(self):
        with pytest.raises(ValueError):
            TypeHandler.create_value("what ever", PatternOptionBuilder.DATE_VALUE)

    def test_create_value_existing_file(self):
        # Create a file
        open('existing-readable.file', 'x').close()

        result = TypeHandler.create_value("existing-readable.file",
            PatternOptionBuilder.EXISTING_FILE_VALUE)
        assert result is not None

        # Clean up
        result.close()
        os.remove("existing-readable.file")

    def test_create_value_existing_file_non_existing_file(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value("non-existing.file", PatternOptionBuilder.EXISTING_FILE_VALUE)

    def test_create_value_file(self):
        result = TypeHandler.create_value("some-file.txt", PatternOptionBuilder.FILE_VALUE)
        assert result.name == "some-file.txt"

    def test_create_value_files(self):
        with pytest.raises(ValueError):
            TypeHandler.create_value("some.files", PatternOptionBuilder.FILES_VALUE)

    def test_create_value_integer_failure(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value("just-a-string", int)

    def test_create_value_number_double(self):
        assert TypeHandler.create_value("1.5", PatternOptionBuilder.NUMBER_VALUE) == 1.5

    def test_create_value_number_long(self):
        assert TypeHandler.create_value("15", PatternOptionBuilder.NUMBER_VALUE) == 15

    def test_create_value_number_no_number(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value("not a number", PatternOptionBuilder.NUMBER_VALUE)

    def test_create_value_object_instantiable_class(self):
        result = TypeHandler.create_value(Instantiable.__name__, PatternOptionBuilder.OBJECT_VALUE)
        assert isinstance(result, Instantiable)

    def test_create_value_object_not_instantiable_class(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value(NotInstantiable.__name__, PatternOptionBuilder.OBJECT_VALUE)

    def test_create_value_object_unknown_class(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value("unknown", PatternOptionBuilder.OBJECT_VALUE)

    def test_create_value_string(self):
        assert TypeHandler.create_value("String", PatternOptionBuilder.STRING_VALUE) == "String"

    def test_create_value_url(self):
        url_string = "https://commons.apache.org"
        result = TypeHandler.create_value(url_string, PatternOptionBuilder.URL_VALUE)
        assert urllib.parse.urlunparse(result) == url_string

    def test_create_value_url_malformed(self):
        with pytest.raises(ParseException):
            TypeHandler.create_value("malformed-url", PatternOptionBuilder.URL_VALUE)
