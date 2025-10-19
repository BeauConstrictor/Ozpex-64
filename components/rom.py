from components.mm_component import MemoryMappedComponent

class Rom(MemoryMappedComponent):
    def __init__(self, min_addr: int, max_addr: int) -> None:
        self.start = min_addr
        self.end = max_addr
        
        self.addresses = bytearray(self.end - self.start + 1)
        
    def load(self, data: list[int], start_addr: int) -> None:
        addr = start_addr
        
        for d in data:
            self.addresses[addr - self.start] = d
            addr += 1
    
    def contains(self, addr: int) -> bool:
        return self.start <= addr <= self.end
    
    def fetch(self, addr: int) -> int:
        return self.addresses[addr - self.start]
    
    def write(self, addr: int, val: int) -> None:
        pass