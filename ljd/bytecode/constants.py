#
# Copyright (C) 2013 Andrian Nord. See Copyright Notice in main.py
#

T_NIL = 0
T_FALSE = 1
T_TRUE = 2


class Table:
    def __init__(self):
        self.array = []

        # Use a list so we can keep the original items order in the
        # table
        self.dictionary = []


class IntegerCdata:
    def __init__(self, bits, unsigned):
        self.bits = bits
        self.unsigned = unsigned

    def __str__(self):
        # Hex literals preserve the exact two's-complement bit pattern, including
        # INT64_MIN and UINT64_MAX, without rounding through a Lua number.
        return "0x%016x%s" % (self.bits, "ULL" if self.unsigned else "LL")


class Constants:
    def __init__(self):
        self.upvalue_references = []
        self.numeric_constants = []
        self.complex_constants = []
