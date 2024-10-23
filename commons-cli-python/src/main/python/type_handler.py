from main.python.pattern_option_builder import PatternOptionBuilder
from main.python.parse_exception import ParseException
import builtins
from main.python.java_handler import java_handler, java_class, input_stream, Types, url


def get_class(classname):
    """
    Throws ValueError if the class could not be found.
    """
    try:
        return globals()[classname]
    except KeyError:
        try:
            return getattr(builtins, classname)
        except AttributeError:
            return java_class(classname)


@java_handler
class TypeHandler:

    def update_namespace_classes(self, namespace: dict):
        for key in namespace.keys():
            if key not in globals().keys() and isinstance(namespace[key], type):
                globals()[key] = namespace[key]
    
    @staticmethod
    def create_class(classname: str):
        """
        Returns the class whose name is classname.
        :param classname: the class name
        :return: The class if it is found
        :raises ParseException: if the class could not be found
        """
        try:
            return get_class(classname)
        except ValueError:
            raise ParseException("Unable to find the class: " + classname)

    @staticmethod
    def create_date(string: str):
        """
        Returns the date represented by str.
        :param string: the date string
        :return: The date if str is a valid date string, otherwise return None.

        :raises ValueError: always
        """
        raise ValueError("Not yet implemented")

    @staticmethod
    def create_file(string: str):
        """
        Returns the File represented by string.
        :param string: the File location
        :return: The file represented by string.
        """
        return Types.File(string)
    
    @staticmethod
    def create_files(string: str):
        """
        Returns the Files represented by string.
        :param string: the Files location
        :return: The files represented by string.

        :raises ValueError: always
        """
        raise ValueError("Not yet implemented")

    @staticmethod
    def create_number(string: str):
        """
        Create a number from a String. If a . is present, it creates a Double, otherwise a Long.
        :param string: the value
        :return: the number represented by string
        :raises ParseException: if string is not a number
        """
        try:
            if "." in string:
                return float(string)
            return int(string)
        except ValueError as e:
            raise ParseException(e.args[0])
        
    @staticmethod
    def create_object(classname: str):
        """
        Create an Object from the classname and empty constructor.
        :param classname: the argument value
        :return: the initialized object
        :raises ParseException: if the class could not be found or the object could not be created
        """
        try:
            clz = get_class(classname)
        except ValueError:
            raise ParseException("Unable to find the class: " + classname)
        try:
            return clz()
        except Exception as e:
            raise ParseException(e.__class__.__name__ + "; Unable to create an instance of: " + classname)
        
    @staticmethod
    def create_url(string: str):
        """
        Returns the URL represented by string.
        :param string: the URL string
        :return: The URL in string is well-formed
        :raises ValueError: if the URL in string is not well-formed
        """
        try:
            return url(string)
        except:
            raise ParseException("Unable to parse the URL: " + string)
    
    @staticmethod
    def create_value(string: str, clazz):
        """
        Returns the Object of type clazz with the value of string.
        :param string: the command line value
        :param clazz: the class representing the type of argument
        :return: The instance of clazz initialized with the value of string.
        :raises ParseException: if the value creation for the given class failed
        """
        if clazz == PatternOptionBuilder.STRING_VALUE:
            return string
        if clazz == PatternOptionBuilder.OBJECT_VALUE:
            return TypeHandler.create_object(string)
        if clazz == PatternOptionBuilder.NUMBER_VALUE:
            return TypeHandler.create_number(string)
        if clazz == PatternOptionBuilder.DATE_VALUE:
            return TypeHandler.create_date(string)
        if clazz == PatternOptionBuilder.CLASS_VALUE:
            return TypeHandler.create_class(string)
        if clazz == PatternOptionBuilder.FILE_VALUE:
            return TypeHandler.create_file(string)
        if clazz == PatternOptionBuilder.EXISTING_FILE_VALUE:
            return TypeHandler.open_file(string)
        if clazz == PatternOptionBuilder.FILES_VALUE:
            return TypeHandler.create_files(string)
        if clazz == PatternOptionBuilder.URL_VALUE:
            return TypeHandler.create_url(string)
        raise ParseException("Unable to handle the class: " + str(clazz))

    @staticmethod
    def open_file(string: str):
        """
        Returns the opened FileInputStream represented by string.
        :param string: the file location
        :return: The file input stream represented by string.
        :raises ParseException: if the file is not exist or not readable
        """
        try:
            return input_stream(string)
        except:
            raise ParseException("Unable to find file: " + string)
