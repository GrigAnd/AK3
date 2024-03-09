from __future__ import annotations

import json
from collections import namedtuple
from enum import Enum


class Opcode(str, Enum):
    LD = "LD"
    ST = "ST"
    SUB = "SUB"
    ADD = "ADD"
    DIVR = "DIVR"
    INC = "INC"
    DEC = "DEC"
    JMP = "JMP"
    JNZ = "JNZ"
    JZ = "JZ"
    JN = "JN"
    HLT = "HLT"
    CLR = "CLR"

    def __str__(self) -> str:
        return self.value


class OperandType(str, Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    NONE = "NONE"

    def __str__(self) -> str:
        return self.value


class Expression(namedtuple("Expression", ["position", "opcode", "operand", "op_type"])):
    def __str__(self) -> str:
        return f"{self.position} {self.opcode} {self.operand} {self.op_type}"


class Data(namedtuple("Data", ["position", "value"])):
    def __str__(self) -> str:
        return f"{self.position} {self.value}"


def write_code(code: list, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        buf = [json.dumps(instr) for instr in code]
        file.write("[" + ",\n".join(buf) + "]")


def write_data(data: list, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        buf = [json.dumps(datum) for datum in data]
        file.write("[" + ",\n".join(buf) + "]")


def read_code(filename: str) -> list:
    with open(filename, encoding="utf-8") as file:
        code = json.load(file)

    instrs = []

    for instr in code:
        instrs.append(instr)

    return instrs


def read_data(filename: str) -> list:
    with open(filename, encoding="utf-8") as file:
        data = json.load(file)

    data_list = []

    for datum in data:
        data_list.append(datum)

    return data_list
