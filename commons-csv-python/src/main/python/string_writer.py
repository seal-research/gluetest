from io import StringIO


class StringWriter(StringIO):
    def __init__(self):
        self.value = ""
        self.is_closed = False
        super().__init__()
    
    def close(self):
        self.value = self.getvalue()
        self.is_closed = True
        super().close()
    
    def getvalue(self) -> str:
        if not self.is_closed:
            return super().getvalue()
        return self.value
