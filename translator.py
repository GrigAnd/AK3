import shlex
import sys

from isa import Opcode, OperandType, write_code, write_data


def clear_line(line: str) -> str:
    return line.split(";")[0].strip()


def value_to_number(value: str) -> int:
    """string hex or int to int"""
    if value.startswith("0x"):
        return int(value, 16)
    return int(value)


def prepare_lines(lines: list) -> list:
    prepared = []
    for line in lines:
        line = clear_line(line)
        if not line:  # empty line
            continue
        prepared.append(line)
    return prepared


def translate(src: str):
    lines = src.splitlines()
    instrs = []
    data = []
    labels = {}
    position = 0
    src_line = 0

    lines = prepare_lines(lines)

    for line in lines:
        src_line += 1

        splitted = shlex.split(line, posix=False)  # split but ignore quotes

        if splitted == ["SECTION", ".text"] or splitted == [
            "SECTION",
            ".data",
        ]:  # new section - reset position (harvard)
            position = 0
            continue

        if line.endswith(":"):  # label
            label = line[:-1]
            assert label not in labels, f"Label {label} already defined"
            labels[label] = position
            continue

        if splitted[0].endswith(":") and splitted[1] == "db":  # data
            label = splitted[0][:-1]
            value = splitted[2]

            assert label not in labels, f"Label {label} already defined"
            labels[label] = position

            if value.startswith('"'):  # string
                position = add_string
                continue

            value = parse_data_arg(value, labels)

            position = parse_buffer(splitted, position, data, src_line, value)

            continue

        opcode, operand = parse_instruction(line)

        instrs.append(
            {"position": position, "opcode": opcode, "operand": operand, "op_type": None, "src_line": src_line}
        )
        position += 1

    parse_indirect_operands(instrs)
    set_labels(instrs, labels)

    return instrs, data


def parse_buffer(splitted: list, position: int, data: list, src_line: int, value: int) -> int:
    if len(splitted) > 3 and splitted[3] == "dup":  # buffer
        count = value
        for _ in range(count):
            add_data(data, position, 0, src_line)
            position += 1
    else:
        add_data(data, position, value, src_line)  # single value
        position += 1

    return position


def parse_data_arg(value: str, labels: dict) -> int:
    if value[0].isdigit():  # number
        return value_to_number(value)

    return labels[value]


def parse_instruction(line: str) -> tuple:
    opcode, *operand = line.split()
    opcode = Opcode(opcode)
    if operand:
        operand = operand[0]
    else:
        operand = None

    if operand and operand[0].isdigit():
        operand = value_to_number(operand)

    return opcode, operand


def add_string(data: list, position: int, value: str, src_line: int) -> None:
    value = value[1:-1]
    add_data(data, position, len(value), src_line)
    position += 1
    for char in value:  # string as array of chars
        add_data(data, position, ord(char), src_line)
        position += 1


def add_data(data: list, position: int, value: int, src_line: int) -> None:
    data.append({"position": position, "value": value, "src_line": src_line})


def parse_indirect_operands(instrs: list) -> None:
    for instr in instrs:  # indirect addressing
        if str(instr["operand"]).startswith("["):
            instr["op_type"] = OperandType.INDIRECT
            instr["operand"] = instr["operand"][1:-1]
        elif instr["operand"] is not None:
            instr["op_type"] = OperandType.DIRECT
        else:
            instr["op_type"] = OperandType.NONE


def set_labels(instrs: list, labels: dict) -> None:
    for instr in instrs:  # replace labels with addresses
        if instr["operand"] in labels:
            label = instr["operand"]
            instr["operand"] = labels[label]

    for instr in instrs:  # check for unknown labels
        if isinstance(instr["operand"], str):
            raise TypeError


def main(input_file: str, data_file: str, code_file: str) -> None:
    with open(input_file, encoding="utf-8") as file:
        src = file.read()

    code, data = translate(src)
    write_code(code, code_file)
    write_data(data, data_file)

    print(f"source LoC: {len(src.splitlines())}, code instrs: {len(code)}, data: {len(data)}")


if __name__ == "__main__":
    assert len(sys.argv) == 4, "Wrong args: translator.py <asm_input_file> <output_data_file> <output_code_file>"
    _, input_file, data_file, code_file = sys.argv
    main(input_file, data_file, code_file)
