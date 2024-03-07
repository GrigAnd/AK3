import sys
import shlex
from typing import List, Tuple
from isa import Opcode, Expression, Data, write_code, write_data


def clear_line(line: str) -> str:
    return line.split(";")[0].strip()


def value_to_number(value: str) -> int:
    if value.startswith("0x"):
        return int(value, 16)
    return int(value)


def translate(src: str):
    lines = src.splitlines()
    instrs = []
    data = []
    labels = {}
    position = 0

    for line in lines:
        line = clear_line(line)
        if not line:
            continue

        splitted = shlex.split(line, posix=False)

        if splitted == ["SECTION", ".text"] or splitted == ["SECTION", ".data"]:
            position = 0
            continue

        if line.endswith(":"):
            label = line[:-1]
            assert label not in labels, f"Label {label} already defined"
            labels[label] = position
            continue

        if splitted[0].endswith(":") and splitted[1] == "db":
            label = splitted[0][:-1]
            value = splitted[2]

            assert label not in labels, f"Label {label} already defined"
            labels[label] = position

            if value.startswith('"'):
                value = value[1:-1]
                data.append(Data(position, len(value)))
                position += 1
                for char in value:
                    data.append(Data(position, ord(char)))
                    position += 1
                continue

            if value[0].isdigit():
                value = value_to_number(value)
            else:
                value = labels[value]

            if len(splitted) > 3 and splitted[3] == "dup":
                count = value
                for _ in range(count):
                    data.append(Data(position, 0))
                    position += 1
            else:
                data.append(Data(position, value))
                position += 1
            continue

        opcode, *operand = line.split()
        opcode = Opcode(opcode)
        if operand:
            operand = operand[0]
        else:
            operand = None

        if operand and operand[0].isdigit():
            operand = value_to_number(operand)

        instrs.append({"position": position, "opcode": opcode, "operand": operand})
        position += 1


    for instr in instrs:
        if str(instr["operand"]).startswith("("):
            instr["opcode"] += "I"
            instr["operand"] = instr["operand"][1:-1]

    for instr in instrs:
        if instr["operand"] in labels:
            label = instr["operand"]
            instr["operand"] = labels[label]

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

    input_file = "hun.asm"
    data_file = "hun_data.json"
    code_file = "hun_code.json"
    main(input_file, data_file, code_file)
