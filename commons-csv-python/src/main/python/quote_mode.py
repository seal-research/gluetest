from enum import Enum


class QuoteMode(Enum):
    ALL = 'ALL'
    ALL_NON_NULL = 'ALL_NON_NULL'
    MINIMAL = 'MINIMAL'
    NON_NUMERIC = 'NON_NUMERIC'
    NONE = 'NONE'
