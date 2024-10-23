from enum import Enum

class Token:

    class Type(Enum):
        INVALID = 0
        TOKEN = 1
        EOF = 2
        EORECORD = 3
        COMMENT = 4

        def __str__(self):
            return self.name
        
        def to_string(self):
            return str(self)
        
        def __eq__(self, other):
            if isinstance(other, Token.Type):
                return self.name == other.name
            elif self.name == other:
                return True
            return False

    def __init__(self, type = Type.INVALID):
        self.type = type
        self.content = ""
        self.is_ready = False

    def reset(self, type = Type.INVALID):
        self.content = ""
        self.type = type
        self.is_ready = False

    def __str__(self):
        # TODO: check if this is correct
        return (f"{Token.Type(self.type).name}"
                f" [{self.content}]")

    def to_string(self):
        return str(self)

    def get_type(self):
        if hasattr(self.type, 'toString'):
            return Token.Type[self.type.toString()]

        return self.type

    def get_content(self):
        return self.content
    
    def set_type(self, type):
        self.type = type
    
    def set_ready(self, is_ready):
        self.is_ready = is_ready
    
    def set_content(self, content):
        self.content = content
    
    def append(self, c):
        """
        Append to the content of the token.
        """
        self.content += c
