from main.python.pretty_list import PrettyList


class CSVRecord:
    EMPTY_STRING_ARRAY = []

    def __init__(
        self,
        values: list = None,
        mapping: dict = None,
        comment: str = None,
        record_number: int = 0,
        character_position: int = 0,
    ):
        self.record_number = record_number
        self._values = PrettyList(
            (values.copy() if hasattr(values, "copy") else values.clone())
            if values is not None
            else CSVRecord.EMPTY_STRING_ARRAY.copy()
        )
        self.mapping = mapping
        self.comment = comment
        self.character_position = character_position

    def get(self, e):
        if isinstance(e, str):
            return self.get_by_name(e)
        elif isinstance(e, int):
            return self._values[e]
        else:
            return self.get_by_enum(e)

    def _get_keys(self):
        if self.mapping == None:
            return []
        if isinstance(self.mapping, dict):
            return list(self.mapping.keys())
        else:
            return list(self.mapping.keySet())

    def get_by_name(self, name: str):
        if self.mapping == None:
            raise ValueError(
                f"No header mapping was specified, the "
                f"record values can't be accessed by name"
            )
        index = self.mapping.get(name)
        index = None if index == None else int(index)
        if index is None:
            raise ValueError(
                f"Mapping for {name} not found, expected one of" f"{self._get_keys()}"
            )
        try:
            return self._values[index]
        except IndexError:
            raise ValueError(
                f"Index for header '{name}' is {index}, but CSVRecord only has"
                f"{self._len_values()} values!"
            )

    def get_by_enum(self, e):
        return self.get_by_name(e.name)

    def get_character_position(self) -> int:
        return self.character_position

    def get_comment(self) -> str:
        return self.comment

    def get_record_number(self) -> int:
        return self.record_number

    def _len_values(self) -> int:
        return (
            self._values.length
            if hasattr(self._values, "length")
            else len(self._values)
            if self._values != None
            else 0
        )

    def is_consistent(self) -> bool:
        len_mapping = (
            self.mapping.size()
            if hasattr(self.mapping, "size")
            else len(self.mapping)
            if self.mapping != None
            else 0
        )

        return self.mapping == None or len_mapping == self._len_values()

    def has_comment(self) -> bool:
        return self.comment != None

    def is_mapped(self, name: str) -> bool:
        return self.mapping != None and name in self.mapping

    def is_set(self, name: str) -> bool:
        return self.is_mapped(name) and self.mapping[name] < self._len_values()

    def __iter__(self) -> iter:
        return iter(self.to_list())

    def __put_in_python(self, map_: dict) -> dict:
        if self.mapping == None:
            return map_
        for name, col in self.mapping.items():
            if col < self._len_values():
                map_[name] = self._values[col]
        return map_

    def __put_in_java(self, map_):
        if self.mapping == None:
            return map_
        if hasattr(self.mapping, "entrySet"):    
            for entry in self.mapping.entrySet():
                name = entry.getKey()
                col = entry.getValue()
                if col < self._len_values():
                    map_[name] = self._values[col]
        else:
            for name, col in self.mapping.items():
                if col < self._len_values():
                    map_[name] = self._values[col]
        return map_

    def put_in(self, map_: dict) -> dict:
        if isinstance(map_, dict):
            return self.__put_in_python(map_)
        else:
            return self.__put_in_java(map_)

    def size(self) -> int:
        return self._len_values()

    def to_list(self) -> list:
        return list(self._values)

    def to_map(self) -> dict:
        return self.put_in({})

    def __str__(self) -> str:
        return (
            f"CSVRecord [comment={self.comment}, mapping={self.mapping}, "
            f"record_number={self.record_number}, values={self._values}]"
        )

    def values(self) -> list:
        return PrettyList(self._values.copy())
