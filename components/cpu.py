from datetime import timedelta
from typing import Optional
from time import sleep

from components.mm_component import MemoryMappedComponent

MAX_ADDR = 65535
ACC_ADDR = -0xacc

def build_word(high: int, low: int) -> int:
    return (high << 8) | low

def get_bit(value, bit):
    return bool(value & (1 << bit))

def parse_twos_complement(val: int) -> int:
    return val - 0x100 if val & 0x80 else val

class Isa:
    def __init__(self, cpu: "Cpu") -> None:
        self.cpu = cpu
        self.opcodes = {
            # http://www.6502.org/users/obelisk/6502/reference.html
            
            0xa9: (self.lda, self.addr_immediate),
            0xa5: (self.lda, self.addr_zero_page),
            0xb5: (self.lda, self.addr_zero_page_x),
            0xad: (self.lda, self.addr_absolute),
            0xbd: (self.lda, self.addr_absolute_x),
            0xb9: (self.lda, self.addr_absolute_y),
            0xa1: (self.lda, self.addr_indexed_indirect),
            0xb1: (self.lda, self.addr_indirect_indexed),
            
            0xa2: (self.ldx, self.addr_immediate),
            0xa6: (self.ldx, self.addr_zero_page),
            0xb6: (self.ldx, self.addr_zero_page_y),
            0xae: (self.ldx, self.addr_absolute),
            0xbe: (self.ldx, self.addr_absolute_y),
            
            0xa0: (self.ldy, self.addr_immediate),
            0xa4: (self.ldy, self.addr_zero_page),
            0xb4: (self.ldy, self.addr_zero_page_x),
            0xac: (self.ldy, self.addr_absolute),
            0xbc: (self.ldy, self.addr_absolute_x),
            
            0x85: (self.sta, self.addr_zero_page),
            0x95: (self.sta, self.addr_zero_page_x),
            0x8d: (self.sta, self.addr_absolute),
            0x9d: (self.sta, self.addr_absolute_x),
            0x99: (self.sta, self.addr_absolute_y),
            0x81: (self.sta, self.addr_indexed_indirect),
            0x91: (self.sta, self.addr_indirect_indexed),
            
            0x86: (self.stx, self.addr_zero_page),
            0x96: (self.stx, self.addr_zero_page_y),
            0x8e: (self.stx, self.addr_absolute),
            
            0x84: (self.sty, self.addr_zero_page),
            0x94: (self.sty, self.addr_zero_page_x),
            0x8c: (self.sty, self.addr_absolute),
            
            0x4c: (self.jmp, self.addr_absolute),
            0x6c: (self.jmp, self.addr_indirect),
            
            0xf0: (self.beq, self.addr_relative),
            
            0xe6: (self.inc, self.addr_zero_page),
            0xf6: (self.inc, self.addr_zero_page_x),
            0xee: (self.inc, self.addr_absolute),
            0xfe: (self.inc, self.addr_absolute_x),
            
            0xe8: (self.inx, None),
            
            0xc8: (self.iny, None),
        }
        
    def addr_immediate(self) -> int:
        addr = self.cpu.pc
        self.cpu.pc += 1
        return addr
    
    def addr_relative(self) -> int:
        offset = parse_twos_complement(self.cpu.fetch(self.cpu.pc))
        self.cpu.pc += 1
        return (self.cpu.pc + offset) & 0xffff
    
    def addr_accumulator(self) -> int:
        return ACC_ADDR
    
    def addr_absolute(self) -> int:
        low = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        high = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        return build_word(high, low)
    
    def addr_absolute_indexed(self, offset) -> int:
        low = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        high = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        
        base = build_word(high, low)
        addr = (base + offset) & 0xffff
        
        return addr
    def addr_absolute_x(self) -> int:
        return self.addr_absolute_indexed(self.cpu.rx)
    def addr_absolute_y(self) -> int:
        return self.addr_absolute_indexed(self.cpu.ry)
    
    def addr_zero_page(self) -> int:
        addr = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        return addr
    
    def addr_zero_page_indexed(self, offset) -> int:
        addr = (self.cpu.fetch(self.cpu.pc) + offset) & 0xff
        self.cpu.pc += 1
        return addr
    def addr_zero_page_x(self) -> int:
        return addr_zero_page_indexed(self.cpu.rx)
    def addr_zero_page_y(self) -> int:
        return addr_zero_page_indexed(self.cpu.ry)
    
    def addr_indexed_indirect(self) -> int:
        operand = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1

        zp_addr = (operand + self.cpu.rx) & 0xff

        low = self.cpu.fetch(zp_addr)
        high = self.cpu.fetch((zp_addr + 1) & 0xff)

        return (high << 8) | low

    def addr_indirect_indexed(self) -> int:
        operand = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1

        low = self.cpu.memory[operand]
        high = self.cpu.memory[(operand + 1) & 0xff]
        base_addr = (high << 8) | low

        addr = (base_addr + self.cpu.ry) & 0xffff

        return addr
    
    def addr_indirect(self) -> int:
        low = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        high = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        ptr = build_word(high, low)
        low_addr = self.cpu.fetch(ptr)
        high_addr = self.cpu.fetch(ptr + 1)
        return build_word(high_addr, low_addr)

    def ld_reg(self, addr: int) -> int:
        value = self.cpu.fetch(addr)
        self.cpu.zero = value == 0
        self.cpu.negative = get_bit(value, 7)
        return value
    def lda(self, addr: int, opcode: int) -> None:
        self.cpu.ra = self.ld_reg(addr)
    def ldx(self, addr: int, opcode: int) -> None:
        self.cpu.rx = self.ld_reg(addr)
    def ldy(self, addr: int, opcode: int) -> None:
        self.cpu.ry = self.ld_reg(addr)
        
    def sta(self, addr: int, opcode: int) -> None:
        self.cpu.write(addr, self.cpu.ra)
    def stx(self, addr: int, opcode: int) -> None:
        self.cpu.write(addr, self.cpu.rx)
    def sty(self, addr: int, opcode: int) -> None:
        self.cpu.write(addr, self.cpu.ry)
        
    def jmp(self, addr: int, opcode: int) -> None:
        self.cpu.pc = addr
        
    def beq(self, addr: int, opcode: int) -> int:
        if self.cpu.zero:
            self.cpu.pc = addr
        
    def add_val(self, val: int, add: int) -> int:
        result = (val + add) & 0xff
        self.cpu.zero = result == 0
        self.cpu.negative = get_bit(result, 7)
        return result
    def inc(self, addr: int, opcode: int) -> None:
        val = self.cpu.fetch(addr)
        val = self.add_val(val, 1)
        self.cpu.write(addr, val)
    def inx(self, addr: int, opcode: int) -> None:
        self.cpu.rx = self.add_val(self.cpu.rx, 1)
    def iny(self, addr: int, opcode: int) -> None:
        self.cpu.ry = self.add_val(self.cpu.ry, 1)

class Cpu:
    def __init__(self, components: dict[str, MemoryMappedComponent]) -> None:
        self.mm_components = components
        
        self.mm_component_map: list[MemoryMappedComponent | None] = []
        for i in range(MAX_ADDR+1):
            component = None
            for c in self.mm_components.values():
                if c.contains(i):
                    component = c
                    break
            self.mm_component_map.append(component)
            
        self.isa = Isa(self)
        
        self.pc = 0x00
        self.sp = 0xfd
        self.ra = 0x00
        self.rx = 0x00
        self.ry = 0x00
        
        self.carry = False
        self.zero = False
        self.interrupt_disable = False
        self.decimal = False
        self.break_flag = False
        self.overflow = False
        self.negative = False
        
    def push_byte(self, val: int) -> None:
        addr = 0x0100 | (self.sp & 0xff)
        self.write(addr, val & 0xff)
        self.sp = (self.sp - 1) & 0xff

    def pop_byte(self) -> int:
        self.sp = (self.sp + 1) & 0xff
        addr = 0x0100 | (self.sp & 0xff)
        return self.fetch(addr)

    def pack_status(self, break_flag_for_push: bool = False) -> int:
        p = 0
        p |= int(self.carry) << 0
        p |= int(self.zero) << 1
        p |= int(self.interrupt_disable) << 2
        p |= int(self.decimal) << 3
        p |= int(break_flag_for_push) << 4
        p |= 1 << 5
        p |= int(self.overflow) << 6
        p |= int(self.negative) << 7
        return p & 0xFF

    def unpack_status(self, p: int) -> None:
        self.carry = bool(p & 0x01)
        self.zero = bool(p & 0x02)
        self.interrupt_disable = bool(p & 0x04)
        self.decimal = bool(p & 0x08)
        self.break_flag = bool(p & 0x10)
        self.overflow = bool(p & 0x40)
        self.negative = bool(p & 0x80)

    def reset(self) -> None:
        low  = self.fetch(0xfffc)
        high = self.fetch(0xfffd)
        self.pc = build_word(high, low)
        
    def resolve_component(self, addr: int) -> MemoryMappedComponent:
        c = self.mm_component_map[addr]
        if c is None: raise IndexError("Unmapped memory area accessed.")
        return c
    
    def fetch(self, addr: int) -> int:
        if addr == ACC_ADDR:
            return self.ra
        
        c = self.resolve_component(addr)
        return c.fetch(addr)
    
    def write(self, addr: int, val: int) -> None:
        if addr == ACC_ADDR:
            self.ra = val
            return
        
        c = self.resolve_component(addr)
        c.write(addr, val)
        
    def decode(self) -> tuple[int, callable, int, int]:
        opcode = self.fetch(self.pc)
        self.pc += 1
        
        if opcode not in self.isa.opcodes:
            raise NotImplementedError(f"Opcode 0x{opcode:02x} not implemented")
        
        instr_func, addr_mode_func = self.isa.opcodes[opcode]
        addr = None if addr_mode_func is None else addr_mode_func()
        
        return addr, instr_func, opcode
    
    def execute(self) -> str:
        addr, instr_func, opcode = self.decode()
        
        instr_func(addr, opcode)
        
        return instr_func.__name__

    def visualise(self, op_name) -> None:
        print(f"Last Instruction")
        print(f"| op:   {op_name}")
        
        def print_reg(name: str, val: int) -> None:
            char_section = "'" + chr(val) + "'" if chr(val).isprintable() else "   "
            print(f"| {name}: ${val:02x} {char_section} {val:3} 0b{val:08b}")
        
        print(f"\nRegisters:")
        print(f"| pc: 0x{self.pc:04x}")
        print_reg("ra", self.ra)
        print_reg("rx", self.rx)
        print_reg("ry", self.ry)
        
        print(f"\nFlags:")
        print(f"| C:{int(self.carry)} Z:{int(self.zero)} " + 
              f"I:{int(self.interrupt_disable)} D:{int(self.decimal)}")
        print(f"| B:{int(self.break_flag)} V:{int(self.overflow)} " + 
              f"N:{int(self.negative)}")