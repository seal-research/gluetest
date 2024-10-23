class PrettyList(list):
    def __str__(self) -> str:
        return f"[{', '.join(map(str, self))}]"
