from collections import namedtuple
import json
from enum import Enum
from typing import List

class Opcode(str, Enum):
    LD = "LD"
    ST = "ST"
    LDI = "LDI"
    STI = "STI"
    DIV = "DIV"
    SUB = "SUB"
    ADD = "ADD"
    INC = "INC"
    DEC = "DEC"
    JMP = "JMP"
    JNZ = "JNZ"
    JZ = "JZ"
    JG = "JG"
    JL = "JL"
    JE = "JE"
    JNE = "JNE"
    HLT = "HLT"
    CLR = "CLR"

    def __str__(self) -> str:
        return self.value

class Expression(namedtuple("Expression", ["position", "opcode", "operand"])):
    def __str__(self) -> str:
        return f"{self.position} {self.opcode} {self.operand}"

class Data(namedtuple("Data", ["position", "value"])):
    def __str__(self) -> str:
        return f"{self.position} {self.value}"

def write_code(code: List[Expression], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        buf = [json.dumps(instr) for instr in code]
        file.write("[" + ",\n".join(buf) + "]")

def write_data(data: List[Data], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        buf = [json.dumps(datum) for datum in data]
        file.write("[" + ",\n".join(buf) + "]")

def read_code(filename: str) -> List[Expression]:
    with open(filename, "r", encoding="utf-8") as file:
        code = json.load(file)

    instrs: List[Expression] = []

    for instr in code:
        opcode = Opcode(instr["opcode"])
        operand = instr["operand"]
        instrs.append(Expression(instr["position"], opcode, operand))

    return instrs

def read_data(filename: str) -> List[Data]:
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    data_list: List[Data] = []

    for datum in data:
        data_list.append(Data(datum["position"], datum["value"]))

    return data_list
