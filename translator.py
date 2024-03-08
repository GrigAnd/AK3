import sys
import shlex
from typing import List, Tuple
from isa import Opcode, OperandType, write_code, write_data


def clear_line(line: str) -> str:
    return line.split(";")[0].strip()

def value_to_number(value: str) -> int:
    """string hex or int to int"""
    if value.startswith("0x"):
        return int(value, 16)
    return int(value)

def translate(src: str):
    lines = src.splitlines()
    instrs = []
    data = []
    labels = {}
    position = 0
    src_line = 0

    for line in lines:
        src_line += 1
        line = clear_line(line)
        if not line: # empty line
            continue

        splitted = shlex.split(line, posix=False) # split but ignore quotes

        if splitted == ["SECTION", ".text"] or splitted == ["SECTION", ".data"]: # new section - reset position (harvard)
            position = 0
            continue

        if line.endswith(":"): # label
            label = line[:-1]
            assert label not in labels, f"Label {label} already defined"
            labels[label] = position
            continue

        if splitted[0].endswith(":") and splitted[1] == "db": # data
            label = splitted[0][:-1]
            value = splitted[2]

            assert label not in labels, f"Label {label} already defined"
            labels[label] = position

            if value.startswith('"'): # string
                value = value[1:-1]
                data.append({"position": position, "value": len(value), "src_line": src_line})
                position += 1
                for char in value: # string as array of chars
                    data.append({"position": position, "value": ord(char), "src_line": src_line})
                    position += 1
                continue

            if value[0].isdigit():
                value = value_to_number(value)
            else:
                value = labels[value]

            if len(splitted) > 3 and splitted[3] == "dup": # buffer
                count = value
                for _ in range(count):
                    data.append({"position": position, "value": 0, "src_line": src_line})
                    position += 1
            else:
                data.append({"position": position, "value": value, "src_line": src_line}) # single value
                position += 1

            continue

        opcode, *operand = line.split() # instruction
        opcode = Opcode(opcode)
        if operand:
            operand = operand[0] # only one operand
        else:
            operand = None

        if operand and operand[0].isdigit():
            operand = value_to_number(operand)

        instrs.append({"position": position, "opcode": opcode, "operand": operand, "op_type": None, "src_line": src_line})
        position += 1


    for instr in instrs: # indirect addressing
        if str(instr["operand"]).startswith("["):
            instr["op_type"] = OperandType.INDIRECT
            instr["operand"] = instr["operand"][1:-1]
        elif instr["operand"] is not None:
            instr["op_type"] = OperandType.DIRECT
        else:
            instr["op_type"] = OperandType.NONE

    for instr in instrs: # replace labels with addresses
        if instr["operand"] in labels:
            label = instr["operand"]
            instr["operand"] = labels[label]

    for instr in instrs: # check for unknown labels
        if isinstance(instr["operand"], str):
            raise ValueError(f"Unknown label in {instr}")


    return instrs, data


def main(input_file: str, data_file: str, code_file: str) -> None:
    with open(input_file, "r", encoding="utf-8") as file:
        src = file.read()

    code, data = translate(src)
    write_code(code, code_file)
    write_data(data, data_file)

    print(
        f"source LoC: {len(src.splitlines())}, code instrs: {len(code)}, data: {len(data)}"
    )


if __name__ == "__main__":
    # assert len(sys.argv) == 4, "Wrong args: translator.py <asm_input_file> <output_data_file> <output_code_file>"
    # _, input_file, data_file, code_file = sys.argv

    input_file = "code.asm"
    data_file = "data.json"
    code_file = "code.json"
    main(input_file, data_file, code_file)
