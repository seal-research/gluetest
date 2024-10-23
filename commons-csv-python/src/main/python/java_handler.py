from enum import Enum

try:
    import java

    class Types:
        String = java.type('java.lang.String')
        Object = java.type('java.lang.Object')
        Number = java.type('java.lang.Number')
        Class = java.type('java.lang.Class')
        Date = java.type('java.util.Date')
        FileInputStream = java.type('java.io.FileInputStream')
        File = java.type('java.io.File')
        Files = java.type('java.io.File[]')
        URL = java.type('java.net.URL')
        Enum = java.type('java.lang.Enum')
        Cursor = java.type('java.sql.ResultSet')
        BufferedReader = java.type('java.io.BufferedReader')

    def java_handler(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                if not isinstance(attr_value, type): # Ignoring inner classes, which are also 'callable'                    
                    setattr(cls, attr_name, type_mapper(attr_value))
        
        # Add a method to identify the classname
        setattr(cls, 'get_class_name', lambda self: cls.__name__)

        return cls
    
    def type_mapper(func):
        """When the identifier for func is called, wrapper is called instead"""
        if isinstance(func, staticmethod):
            def wrapper(*args, **kwargs):
                args_processed = tuple([type_map(arg) for arg in args])
                kwargs_processed = {key: type_map(value) for key, value in kwargs.items()}

                return func(*args_processed, **kwargs_processed)

            return staticmethod(wrapper)
        else:
            def wrapper(self, *args, **kwargs):
                args_processed = tuple([type_map(arg) for arg in args])
                kwargs_processed = {key: type_map(value) for key, value in kwargs.items()}

                # Bound function call to prevent recursion
                return func.__get__(self, type(self))(*args_processed, **kwargs_processed)
        
            return wrapper
    
    def type_map(arg):
        # Noneify
        if arg == None:
            return None
        
        # get underlying python objects from java objects
        if hasattr(arg, 'getPythonObject'):
            return arg.getPythonObject()
        
        # handle Java types (convert from foreign to python)
        # Checking for type foreign is safe because strings have not been observed
        # to have the foreign type
        try:
            if type(arg).__name__ == 'foreign' and str(arg).startswith("java."):
                return java.type(str(arg))
        except:
            pass

        # Handle Java Properties
        if type(arg).__name__ == 'foreign' and hasattr(arg, 'getProperty'):
            D = dict()
            for key in arg.propertyNames():
                D[key] = arg.getProperty(key)
            return D

        return arg

    # Override isinstance to handle python objects with type foreign
    _isinstance = isinstance
    def isinstance(obj, cls):
        if _isinstance(obj, cls):
            return True
        if hasattr(obj, 'get_class_name'):
            return obj.get_class_name() == cls.__name__
        return False
    
    # Check for java class names and return the corresponding java class if found
    def java_class(classname: str):
        try:
            return java.type(classname)
        except:
            raise ValueError()
    
    def convert_to_python_enum(enum: Types.Enum, target: Enum):
        name = enum.name()
        return getattr(target, name)
    
    # Create an input stream
    def input_stream(file: str):
        return java.type('java.io.FileInputStream')(file)
    
    def url(string: str):
        return java.type('java.net.URL')(string)

except:
    import datetime
    import io
    import pathlib
    import urllib
    import sqlite3

    def java_handler(cls):
        return cls

    class Types:
        String = str
        Object = object
        Number = int
        Class = type
        Date = datetime.datetime
        FileInputStream = io.TextIOWrapper
        File = pathlib.Path
        Files = list[pathlib.Path]
        URL = urllib.parse.ParseResult
        Enum = Enum
        Cursor = sqlite3.Cursor
        BufferedReader = io.StringIO # unused in this case

    _isinstance = isinstance
    def isinstance(obj, cls):
        return _isinstance(obj, cls)

    def java_class(classname: str):
        raise ValueError()
    
    def input_stream(file):
        return open(file)
    
    def convert_to_python_enum(enum, target):
        return enum
    
    def url(string: str):
        result = urllib.parse.urlparse(string)

        # Some checks: Are these sufficient?
        if not all([result.scheme, result.netloc]):
            raise urllib.error.URLError("Invalid URL")
        if not result.scheme in ["http", "https", "ftp", "nntp", "file", "jar"]:
            raise urllib.error.URLError("Unsupported URL scheme")

        return result
