from components.mm_component import MemoryMappedComponent

class Ram(MemoryMappedComponent):
    def __init__(self, min_addr: int, max_addr: int) -> None:
        self.start = min_addr
        self.end = max_addr
        
        self.addresses = bytearray(self.end - self.start + 1)
        
    def load(self, data: list[int], start_addr: int) -> None:
        addr = start_addr
        
        for d in data:
            print(f"writing 0x{addr:04x}")
            self.write(addr, d)
            addr += 1
    
    def contains(self, addr: int) -> bool:
        return self.start <= addr <= self.end
    
    def fetch(self, addr: int) -> int:
        return self.addresses[addr - self.start] & 0xff
    
    def write(self, addr: int, val: int) -> None:
        self.addresses[addr - self.start] = val & 0xff