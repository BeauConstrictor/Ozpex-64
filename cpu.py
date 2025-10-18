from datetime import timedelta
from time import sleep

from mm_component import MemoryMappedComponent
from ram import Ram
from serial import SerialOutput

# TODO:
# Support D (decimal) flag in ADC

MAX_ADDR = 65535
CLOCK_INTERVAL = timedelta(milliseconds=10)

def two_bytes_to_word(high: int, low: int) -> int:
    return (high << 8) | low


class Isa:
    def __init__(self, cpu: "Cpu") -> None:
        self.cpu = cpu
        
        self.opcodes = {
            0xa9: (self.lda, self.addr_immediate, 2),
            0xa5: (self.lda, self.addr_zero_page, 3),
            0xb5: (self.lda, self.addr_zero_page_x, 4),
            0x8d: (self.sta, self.addr_absolute, 4),
            0xea: (self.nop, None, 2),
            0x18: (self.clc, None, 2),
            0x69: (self.adc, self.addr_immediate, 2),
            0x4c: (self.jmp, self.addr_absolute, 3),
            0x6c: (self.jmp, self.addr_indirect, 5),
            0xE8: (self.inx, None, 2),
            0xcA: (self.dex, None, 2),
            0xa2: (self.ldx, self.addr_immediate, 2),
            0xf0: (self.beq, self.addr_relative, 2),
        }
        
    def addr_relative(self) -> int:
        offset = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        if offset & 0x80:
            offset -= 0x100
        return self.cpu.pc + offset
        
    def addr_immediate(self) -> int:
        addr = self.cpu.pc
        self.cpu.pc += 1
        return addr
    
    def addr_absolute(self) -> int:
        low = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        high = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        return two_bytes_to_word(high, low)
    
    def addr_indirect(self) -> int:
        ptr_low = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        ptr_high = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        ptr = two_bytes_to_word(ptr_high, ptr_low)
        
        low = self.cpu.fetch(ptr)
        high = self.cpu.fetch((ptr & 0xFF00) | ((ptr + 1) & 0x00FF))  # old bug.
        return two_bytes_to_word(high, low)
    
    def addr_zero_page(self) -> int:
        addr = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        return addr
        
    def addr_zero_page_x(self) -> int:
        base = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        addr = (base + self.cpu.rx) & 0xFF
        return addr
    
    def addr_zero_page_y(self) -> int:
        base = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        addr = (base + self.cpu.ry) & 0xFF
        return addr
        
    def lda(self, addr: int, opcode: int) -> None:
        value = self.cpu.fetch(addr)
        self.cpu.ra = value
        self.cpu.zero = (value == 0)
        self.cpu.negative = (value & 0x80) != 0
        
    def ldx(self, addr: int, opcode: int) -> None:
        value = self.cpu.fetch(addr)
        self.cpu.ra = value
        self.cpu.zero = (value == 0)
        self.cpu.negative = (value & 0x80) != 0
        
    def sta(self, addr: int, opcode: int) -> None:
        self.cpu.write(addr, self.cpu.ra)
        
    def nop(self, addr: int, opcode: int) -> None:
        return None
    
    def clc(self, addr: int, opcode: int) -> None:
        self.cpu.carry = False
        
    def jmp(self, addr: int, opcode: int) -> None:
        self.cpu.pc = addr
        
    def adc(self, addr: int, opcode: int) -> None:
        value = self.cpu.fetch(addr)
        result = self.cpu.ra + value + (1 if self.cpu.carry else 0)
        
        self.cpu.carry = result > 0xFF
        self.cpu.zero = (result & 0xFF) == 0
        self.cpu.negative = (result & 0x80) != 0
        self.cpu.overflow = (~(self.cpu.ra ^ value) & (self.cpu.ra ^ result) & 0x80) != 0
        
        self.cpu.ra = result & 0xFF
        
    def inx(self, addr, opcode):
        self.cpu.rx = (self.cpu.rx + 1) & 0xFF
        self.cpu.zero = self.cpu.rx == 0
        self.cpu.negative = (self.cpu.rx & 0x80) != 0

    def dex(self, addr, opcode):
        self.cpu.rx = (self.cpu.rx - 1) & 0xFF
        self.cpu.zero = self.cpu.rx == 0
        self.cpu.negative = (self.cpu.rx & 0x80) != 0
        
    def beq(self, addr, opcode):
        if self.cpu.zero:
            self.cpu.pc += addr

class Cpu:
    def __init__(self) -> None:
        self.mm_components = {
            "ram": Ram(0x0000, 0xfffe),
            "serial": SerialOutput(0xffff),
        }
        
        self.mm_component_map: list[MemoryMappedComponent | None] = []
        for i in range(MAX_ADDR+1):
            component = None
            for c in self.mm_components.values():
                if c.contains(i):
                    component = c
                    break
            self.mm_component_map.append(component)
            
        self.clock_interval_secs = CLOCK_INTERVAL.total_seconds()
        self.isa = Isa(self)
        
        self.pc = 0
        self.ra = 0
        self.rx = 0
        self.ry = 0
        
        self.carry = False
        self.zero = False
        self.interrupt_disable = False
        self.decimal = False
        self.break_flag = False
        self.overflow = False
        self.negative = False
        
    def reset(self) -> None:
        low  = self.fetch(0xFFFC)
        high = self.fetch(0xFFFD)
        self.pc = two_bytes_to_word(high, low)
        
    def clock_pause(self, cycles: int) -> None:
        sleep(self.clock_interval_secs * cycles)
        
    def resolve_component(self, addr: int) -> MemoryMappedComponent:
        c = self.mm_component_map[addr]
        if c is None: raise IndexError("Unmapped memory area accessed.")
        return c
    
    def fetch(self, addr: int) -> int:
        c = self.resolve_component(addr)
        return c.fetch(addr)
    
    def write(self, addr: int, val: int) -> None:
        c = self.resolve_component(addr)
        c.write(addr, val)
        
    def decode(self) -> tuple[int, callable, int, int]:
        opcode = self.fetch(self.pc)
        self.pc += 1
        
        if opcode not in self.isa.opcodes:
            raise NotImplementedError(f"Opcode ${opcode:02x} not implemented")
        
        instr_func, addr_mode_func, cycles_pause = self.isa.opcodes[opcode]
        addr = None if addr_mode_func is None else addr_mode_func()
        
        return addr, instr_func, cycles_pause, opcode
    
    def execute(self) -> str:
        addr, instr_func, cycles_pause, opcode = self.decode()
        
        instr_func(addr, opcode)
        self.clock_pause(cycles_pause)
        
        return instr_func.__name__

    def visualise(self, op_name) -> None:
        print(f"Last instruction: ")
        print(f"+-----------+")
        print(f"| op:   {op_name} |")
        print(f"+-----------+")
        
        print(f"\nRegisters:")
        print(f"+-----------+")
        print(f"| pc: ${self.pc:04x} |")
        print(f"| ra:   ${self.ra:02x} |")
        print(f"| rx:   ${self.rx:02x} |")
        print(f"| ry:   ${self.ry:02x} |")
        print(f"+-----------+")
        
        print(f"\nFlags:")
        print(f"+-----------------+")
        print(f"| C:{int(self.carry)} Z:{int(self.zero)} " + 
              f"I:{int(self.interrupt_disable)} D:{int(self.decimal)} |")
        print(f"| B:{int(self.break_flag)} V:{int(self.overflow)} " + 
              f"N:{int(self.negative)}     |")
        print(f"+-----------------+")