from datetime import timedelta
from typing import Optional
from time import sleep

from components.mm_component import MemoryMappedComponent

MAX_ADDR = 65535
ACC_ADDR = -0xacc

def build_word(high: int, low: int) -> int:
    return (high << 8) | low

def break_word(word: int) -> tuple[int, int]:
    low = word & 0xff
    high = (word >> 8) & 0xff
    return high, low

def get_bit(value, bit):
    return bool(value & (1 << bit))

def parse_twos_complement(val: int) -> int:
    return val - 0x100 if val & 0x80 else val

class Isa:
    def __init__(self, cpu: "Cpu") -> None:
        self.cpu = cpu
        self.opcodes = {
            # http://www.6502.org/users/obelisk/6502/reference.html
            
            0xea: (self.nop, None),
            
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
            0xd0: (self.bne, self.addr_relative),
            
            0xe6: (self.inc, self.addr_zero_page),
            0xf6: (self.inc, self.addr_zero_page_x),
            0xee: (self.inc, self.addr_absolute),
            0xfe: (self.inc, self.addr_absolute_x),
            
            0xe8: (self.inx, None),
            0xc8: (self.iny, None),
            
            0x20: (self.jsr, self.addr_absolute),
            0x60: (self.rts, None),
            
            0xc9: (self.cmp, self.addr_immediate),
            0xc5: (self.cmp, self.addr_zero_page),
            0xd5: (self.cmp, self.addr_zero_page_x),
            0xcd: (self.cmp, self.addr_absolute),
            0xdd: (self.cmp, self.addr_absolute_x),
            0xd9: (self.cmp, self.addr_absolute_y),
            0xc1: (self.cmp, self.addr_indexed_indirect),
            0xd1: (self.cmp, self.addr_indirect_indexed),
            
            0xe0: (self.cpx, self.addr_immediate),
            0xe4: (self.cpx, self.addr_zero_page),
            0xec: (self.cpx, self.addr_absolute),
            
            0xc0: (self.cpy, self.addr_immediate),
            0xc4: (self.cpy, self.addr_zero_page),
            0xcc: (self.cpy, self.addr_absolute),
            
            0x69: (self.adc, self.addr_immediate),
            0x65: (self.adc, self.addr_zero_page),
            0x75: (self.adc, self.addr_zero_page_x),
            0x6d: (self.adc, self.addr_absolute),
            0x7d: (self.adc, self.addr_absolute_x),
            0x79: (self.adc, self.addr_absolute_y),
            0x61: (self.adc, self.addr_indexed_indirect),
            0x71: (self.adc, self.addr_indirect_indexed),
            
            0xe9: (self.sbc, self.addr_immediate),
            0xe5: (self.sbc, self.addr_zero_page),
            0xf5: (self.sbc, self.addr_zero_page_x),
            0xed: (self.sbc, self.addr_absolute),
            0xfd: (self.sbc, self.addr_absolute_x),
            0xf9: (self.sbc, self.addr_absolute_y),
            0xe1: (self.sbc, self.addr_indexed_indirect),
            0xf1: (self.sbc, self.addr_indirect_indexed),
            
            0x38: (self.sec, None),
            0x18: (self.clc, None),
            
            0xf8: (self.sed, None),
            0xd8: (self.cld, None),
            
            0x78: (self.sei, None),
            0x58: (self.cli, None),
            
            0xb8: (self.clv, None),
            
            0x98: (self.tya, None),
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
        return self.addr_zero_page_indexed(self.cpu.rx)
    def addr_zero_page_y(self) -> int:
        return self.addr_zero_page_indexed(self.cpu.ry)
    
    def addr_indexed_indirect(self) -> int:
        operand = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1

        zp_addr = (operand + self.cpu.rx) & 0xff

        low = self.cpu.fetch(zp_addr)
        high = self.cpu.fetch((zp_addr + 1) & 0xff)

        return build_word(high, low)

    def addr_indirect_indexed(self) -> int:
        operand = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1

        low = self.cpu.fetch(operand)
        high = self.cpu.fetch((operand + 1) & 0xff)
        base_addr = build_word(high, low)

        return (base_addr + self.cpu.ry) & 0xffff
    
    def addr_indirect(self) -> int:
        low = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        high = self.cpu.fetch(self.cpu.pc)
        self.cpu.pc += 1
        ptr = build_word(high, low)
        low_addr = self.cpu.fetch(ptr)
        high_addr = self.cpu.fetch(ptr + 1)
        return build_word(high_addr, low_addr)
    
    def nop(self, addr: int, opdcode: int) -> None:
        return sleep(0.01)

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
    def bne(self, addr: int, opcode: int) -> int:
        if not self.cpu.zero:
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
        
    def jsr(self, addr: int, opcode: int) -> None:
        rts_bytes = break_word(self.cpu.pc - 1) # or is it + 1?
        self.cpu.push_byte(rts_bytes[1])
        self.cpu.push_byte(rts_bytes[0])
        self.cpu.pc = addr
        
    def rts(self, addr: int, opcode: int) -> None:
        rts_addr = build_word(self.cpu.pop_byte(), self.cpu.pop_byte())
        self.cpu.pc = rts_addr + 1 # or is it - 1?
        
    def cp_reg(self, reg: int, addr: int) -> None:
        m = self.cpu.fetch(addr)
        self.cpu.carry = reg >= m
        self.cpu.zero = reg == m
        self.cpu.negative = get_bit(reg-m, 7)
    def cmp(self, addr: int, opcode: int) -> None:
        self.cp_reg(self.cpu.ra, addr)
    def cpx(self, addr: int, opcode: int) -> None:
        self.cp_reg(self.cpu.rx, addr)
    def cpy(self, addr: int, opcode: int) -> None:
        self.cp_reg(self.cpu.ry, addr)
        
    def adc_sbc(self, addr: int, opcode: int, sbc: bool) -> None:
        if self.cpu.decimal:
            raise NotImplementedError("Decimal mode is not implemented.")
        
        a = self.cpu.ra
        b = self.cpu.fetch(addr)
        if sbc: b ^= 0xff

        s = a + b + self.cpu.carry
        self.cpu.carry = s > 0xff
        s &= 0xff
        self.cpu.zero = s == 0
        self.cpu.negative = get_bit(s, 7)

        if sbc: self.cpu.overflow = ((a ^ s) & (~b ^ s) & 0x80) != 0
        else: self.cpu.overflow = ((a ^ s) & (b ^ s) & 0x80) != 0
            
        self.cpu.ra = s
    def adc(self, addr: int, opcode: int) -> None:
        self.adc_sbc(addr, opcode, sbc=False)
    def sbc(self, addr: int, opcode: int) -> None:
        self.adc_sbc(addr, opcode, sbc=True)
        
    def sec(self, addr: int, opcode: int) -> None:
        self.cpu.carry = True
    def clc(self, addr: int, opcode: int) -> None:
        self.cpu.carry = False
        
    def sed(self, addr: int, opcode: int) -> None:
        self.cpu.decimal = True
    def cld(self, addr: int, opcode: int) -> None:
        self.cpu.decimal = False
        
    def sei(self, addr: int, opcode: int) -> None:
        self.cpu.interrupt_disable = True
    def cli(self, addr: int, opcode: int) -> None:
        self.cpu.interrupt_disable = False
        
    def clv(self, addr: int, opcode: int) -> None:
        self.cpu.overflow = False
        
    def tya(self, addr: int, opcode: int) -> None:
        self.cpu.zero = self.cpu.ra == 0
        self.cpu.negative = get_bit(self.cpu.ra, 7)
        self.cpu.ra = self.cpu.ry


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