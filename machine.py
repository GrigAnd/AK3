import logging
import sys

from isa import Opcode, OperandType, read_code, read_data

class DataPath:
  data_memory = None
  data_memory_size = None
  data_address = None
  acc = None

  input_buffer = None
  output_buffer = None

  in_addr = None
  out_addr = None

  def __init__(self, data_memory_size: int, input_buffer: list, in_addr: int, out_addr: int) -> None:
    self.data_memory_size = data_memory_size
    self.data_memory = [0] * data_memory_size
    self.data_address = 0
    self.acc = 0
    self.input_buffer = input_buffer
    self.output_buffer = []
    self.in_addr = in_addr
    self.out_addr = out_addr


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

    def do_instruction(self) -> None:
        instr = self.program_memory[self.pc]
        opcode = instr["opcode"]

        match opcode:
            case Opcode.HLT:
                raise StopIteration
            case Opcode.JMP:
                self.latch_pc(True)
            case Opcode.JZ:
                self.data_path.latch_acc()
                self.tick()

                if self.data_path.is_z():
                    self.latch_pc(True)
                else:
                    self.latch_pc(False)
                self.tick()
            case Opcode.CLR:
                self.data_path.clr_acc()
                self.latch_pc(False)
                self.tick()
            case Opcode.LD:
                self.data_path.input = instr["operand"]
                self.data_path.da_mux("input")
                self.data_path.eo()
                self.data_path.latch_acc()
                self.tick()

                if instr["op_type"] == OperandType.INDIRECT:
                    self.data_path.da_mux("acc")
                    self.data_path.eo()
                    self.data_path.latch_acc()
                    self.tick()
                
                self.latch_pc(False)

            case Opcode.ST:
                self.data_path.input = instr["operand"]
                self.data_path.da_mux("input")
                self.data_path.wr()
                self.tick()

                if instr["op_type"] == OperandType.INDIRECT:
                    self.data_path.latch_acc()
                    self.data_path.da_mux("acc")
                    self.data_path.wr()
                    self.tick()

                self.latch_pc(False)

            case Opcode.INC:
                self.data_path.latch_acc()
                self.data_path.add_1()
                self.tick()

                self.latch_acc()
                self.tick()

                self.latch_pc(False)

            case Opcode.DEC:
                self.data_path.latch_acc()
                self.data_path.sub_1()
                self.tick()

                self.latch_acc()
                self.tick()

                self.latch_pc(False)
                

            







    def __repr__(self) -> str:
        repr = "TICK: {:3} PC: {:3} ACC: {:3} MEM: {:3} ADDR: {:3}".format(
            self.get_tick(),
            self.pc,
            self.data_path.acc,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.data_address,
        )
        # TODO
        return repr

    



def run(
    code: list,
    data: list,
    input_buffer: list,
    data_memory_size: int,
    in_addr: int,
    out_addr: int,
    limit: int,
) -> tuple:
   
    dp = DataPath(data_memory_size, input_buffer, in_addr, out_addr)
    cu = ControlUnit(code, dp)
    instr_count = 0

    try:
        while instr_count < limit:
            cu.do()
            instr_count += 1
    except StopIteration: 
        pass
    except EOFError:
        logging.debug("EOF")
          


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
       in_addr=254,
       out_addr=255,
       limit=1000
    )

    print("".join(out))
    print(f"Instructions executed: {instr_count}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 4, "Wrong args: machine.py <code_file> <data_file> <input_file>"
    _, code_file, data_file, input_file = sys.argv
