from enum import Enum
import logging

from isa import Opcode, OperandType, read_code, read_data


class ALU(str, Enum):
    ADD = "ADD"
    SUB = "SUB"
    DIVR = "DIVR"
    DIRECT = "DIRECT"
    INC = "INC"
    DEC = "DEC"
    CLR = "CLR"

    def __str__(self) -> str:
        return self.value

    def get_lambda(self):
        match self:
            case ALU.ADD:
                return lambda dp: dp.acc + dp.alu_right
            case ALU.SUB:
                return lambda dp: dp.acc - dp.alu_right
            case ALU.DIVR:
                return lambda dp: dp.acc % dp.alu_right
            case ALU.DIRECT:
                return lambda dp: dp.alu_right
            case ALU.INC:
                return lambda dp: dp.acc + 1
            case ALU.DEC:
                return lambda dp: dp.acc - 1
            case ALU.CLR:
                return lambda dp: 0


class DataPath:
    data_memory = None
    data_memory_size = None
    data_address = None
    acc = None

    input_buffer = None
    output_buffer = None

    in_addr = None
    out_addr = None

    alu_right: int = 0

    is_indirect: bool = None

    alu_mode = ALU.DIRECT

    def __init__(
        self,
        data_memory,
        data_memory_size: int,
        input_buffer: list,
        in_addr: int,
        out_addr: int,
    ) -> None:
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        for data in data_memory:
            self.data_memory[data["position"]] = data["value"]
        self.data_address = 0
        self.acc = 0
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.in_addr = in_addr
        self.out_addr = out_addr
        self.is_indirect = False

    def latch_acc(self) -> None:
        self.acc = ALU.get_lambda(self.alu_mode)(self)

    def is_z(self) -> bool:
        return self.acc == 0

    def is_n(self) -> bool:
        return self.acc < 0

    def eo(self) -> None:
        eo_in, _ = self.decode_address()

        if eo_in:
            self.alu_right = self.get_io()
        else:
            self.alu_right = self.data_memory[self.data_address]

    def wr(self) -> None:
        data = self.acc

        _, wr_out = self.decode_address()

        if wr_out:
            self.set_io(data)
        else:
            self.data_memory[self.data_address] = data

    def get_io(self) -> int:
        try:
            char = self.input_buffer.pop(0)
            return ord(char)
        except IndexError:
            raise EOFError

    def set_io(self, value: int) -> None:
        self.output_buffer.append(chr(value))

    def decode_address(self) -> tuple:
        """Returns (is_in, is_out) tuple."""
        match self.data_address:
            case self.in_addr:
                return (True, False)
            case self.out_addr:
                return (False, True)
            case _:
                return (False, False)


class ControlUnit:
    program_memory = None
    data_path = None
    pc = None

    _tick = None

    def __init__(self, program_memory: list, data_path: DataPath) -> None:
        self.program_memory = program_memory
        self.data_path = data_path
        self.pc = 0
        self._tick = 0

    def tick(self) -> None:
        self._tick += 1

    def get_tick(self) -> int:
        return self._tick

    def latch_pc(self, is_jmp: bool) -> None:
        if is_jmp:
            instr = self.program_memory[self.pc]
            assert "operand" in instr, f"Need operand in: {instr}"
            self.pc = instr["operand"]
        else:
            self.pc += 1

    def do(self) -> None:
        if self.pc >= len(self.program_memory):
            raise StopIteration

        instr = self.program_memory[self.pc]
        opcode = instr["opcode"]

        match opcode:
            case Opcode.HLT:
                raise StopIteration

            case Opcode.JMP:
                self.latch_pc(True)

            case Opcode.JZ:
                self.tick()
                if self.data_path.is_z():
                    self.latch_pc(True)
                else:
                    self.latch_pc(False)
                self.tick()

            case Opcode.JNZ:
                self.tick()
                if not self.data_path.is_z():
                    self.latch_pc(True)
                else:
                    self.latch_pc(False)

            case Opcode.JN:
                self.tick()
                if self.data_path.is_n():
                    self.latch_pc(True)
                else:
                    self.latch_pc(False)

            case Opcode.CLR:
                self.data_path.alu_mode = ALU.CLR
                self.data_path.latch_acc()
                self.tick()
                self.latch_pc(False)

            case Opcode.LD:
                self.data_path.data_address = instr["operand"]
                self.data_path.eo()
                self.data_path.alu_mode = ALU.DIRECT
                self.data_path.latch_acc()
                self.tick()
                if instr["op_type"] == OperandType.INDIRECT:
                    self.data_path.data_address = self.data_path.acc
                    self.data_path.eo()
                    self.data_path.alu_mode = ALU.DIRECT
                    self.data_path.latch_acc()
                    self.tick()
                self.latch_pc(False)

            case Opcode.ST:
                if instr["op_type"] == OperandType.DIRECT:
                    self.data_path.data_address = instr["operand"]
                    self.data_path.wr()
                    self.tick()
                elif instr["op_type"] == OperandType.INDIRECT:
                    self.data_path.data_address = instr["operand"]
                    self.data_path.eo()
                    self.tick()
                    self.data_path.data_address = self.data_path.alu_right
                    self.data_path.wr()
                    self.tick()
                self.latch_pc(False)

            case Opcode.INC:
                self.data_path.alu_mode = ALU.INC
                self.tick()
                self.data_path.latch_acc()
                self.tick()
                self.latch_pc(False)

            case Opcode.DEC:
                self.data_path.alu_mode = ALU.DEC
                self.tick()
                self.data_path.latch_acc()
                self.tick()
                self.latch_pc(False)

            case Opcode.SUB:
                self.data_path.data_address = instr["operand"]
                self.data_path.eo()
                self.tick()
                self.data_path.alu_mode = ALU.SUB
                self.data_path.latch_acc()
                self.latch_pc(False)

            case Opcode.ADD:
                self.data_path.data_address = instr["operand"]
                self.data_path.eo()
                self.tick()
                self.data_path.alu_mode = ALU.ADD
                self.data_path.latch_acc()
                self.latch_pc(False)

            case Opcode.DIVR:
                self.data_path.data_address = instr["operand"]
                self.data_path.eo()
                self.tick()
                self.data_path.alu_mode = ALU.DIVR
                self.data_path.latch_acc()
                self.latch_pc(False)

    def __repr__(self) -> str:
        repr = "TICK: {:3} PC: {:3} ACC: {:3} MEM: {:3} ADDR: {:3}".format(
            self.get_tick() if self.get_tick() is not None else "N/A",
            self.pc if self.pc is not None else "N/A",
            self.data_path.acc if self.data_path.acc is not None else "N/A",
            (
                self.data_path.data_memory[self.data_path.data_address]
                if self.data_path.data_address < len(self.data_path.data_memory)
                and self.data_path.data_memory[self.data_path.data_address] is not None
                else "N/A"
            ),
            (self.data_path.data_address if self.data_path.data_address is not None else "N/A"),
        )
        # TODO

        instr = self.program_memory[self.pc - 1]
        opcode = instr["opcode"]
        instr_repr = str(opcode)

        if "arg" in instr:
            instr_repr += " {}".format(instr["arg"])

        if "term" in instr:
            term = instr["term"]
            instr_repr += "  ('{}'@{}:{})".format(term.symbol, term.line, term.pos)

        return "{} \t{}".format(repr, instr_repr)


def run(
    code: list,
    data: list,
    input_buffer: list,
    data_memory_size: int,
    in_addr: int,
    out_addr: int,
    limit: int,
) -> tuple:
    dp = DataPath(data, data_memory_size, input_buffer, in_addr, out_addr)
    cu = ControlUnit(code, dp)
    instr_count = 0

    try:
        while instr_count < limit:
            cu.do()
            instr_count += 1
            logging.debug("%s", cu)
    except StopIteration:
        pass
    except EOFError:
        logging.debug("EOF")

    return dp.output_buffer, instr_count


def main(input_file: str, data_file: str, code_file: str) -> None:
    code = read_code(code_file)
    data = read_data(data_file)

    with open(input_file, "r", encoding="utf-8") as file:
        input_text = file.read()
        tokens = []
        for char in input_text:
            tokens.append(char)

    out, instr_count = run(
        code,
        data,
        tokens,
        data_memory_size=100,
        in_addr=4343,
        out_addr=4242,
        limit=200000000,
    )

    print("".join(out))
    print(f"Instructions executed: {instr_count}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    # assert len(sys.argv) == 4, "Wrong args: machine.py <code_file> <data_file> <input_file>"
    # _, code_file, data_file, input_file = sys.argv
    code_file = "./translated/code.json"
    data_file = "./translated/data.json"
    input_file = "./input.txt"

    main(input_file, data_file, code_file)
