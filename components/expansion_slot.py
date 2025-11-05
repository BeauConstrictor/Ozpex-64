from typing import Callable
import os.path

from components.mm_component import MemoryMappedComponent

class ExpansionSlot(MemoryMappedComponent):
    def __init__(self, min_addr: int, max_addr: int) -> None:
        self.start = min_addr
        self.end = max_addr
        
        self.mount_read  = None
        self.mount_write = None
        
    def mount(self, read: Callable[[int], int], write: Callable[[int, int], None]) -> None:
        self.mount_read  = read
        self.mount_write = write
    
    def contains(self, addr: int) -> bool:
        return self.start <= addr <= self.end
    
    def fetch(self, addr: int) -> int:
        if self.mount_read is None: return 0x00
        return self.mount_read(addr - self.start)
    
    def write(self, addr: int, val: int) -> None:
        if self.mount_write is None: return
        self.mount_write(addr - self.start, val)
        
class RomExpansion:
    def __init__(self, name: str) -> None:
        path = os.path.join("roms", name + ".bin")
        
        self.addresses = bytearray(0x2000)
        
        with open(path, "rb") as f:
            data = f.read()
        addr = 0
        for d in data:
            self.addresses[addr] = d
            addr += 1
        
    def read(self, addr: int) -> int:
        return self.addresses[addr] & 0xff
    
    def write(self, addr: int, val: int) -> None:
        pass

class RamExpansion:
    def __init__(self, name: str) -> None:
        self.path = os.path.join("roms", name + ".bin")
        self.addresses = bytearray(0x2000)

    def read(self, addr: int) -> int:
        return self.addresses[addr] & 0xff

    def write(self, addr: int, val: int) -> None:
        self.addresses[addr] = val & 0xff
    
class BbRamExpansion:
    def __init__(self, name: str) -> None:
        self.path = name
        self.addresses = bytearray(0x2000)

        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                data = f.read()
            self.addresses[:len(data)] = data
        else:
            with open(self.path, "wb") as f:
                f.write(self.addresses)

    def read(self, addr: int) -> int:
        return self.addresses[addr] & 0xff

    def write(self, addr: int, val: int) -> None:
        self.addresses[addr] = val & 0xff
        with open(self.path, "r+b") as f:
            f.seek(addr)
            f.write(bytes([val & 0xff]))
