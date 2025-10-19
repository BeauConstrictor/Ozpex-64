from typing import Callable

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