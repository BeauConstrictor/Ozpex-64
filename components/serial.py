from components.mm_component import MemoryMappedComponent

from sys import stdout

class SerialOutput(MemoryMappedComponent):
    def __init__(self, addr: int) -> None:
        self.addr = addr
        
    def contains(self, addr: int) -> bool:
        return addr == self.addr
    
    def fetch(self, addr: int) -> int:
        return 0x00
    
    def write(self, addr: int, val: int) -> None:
        if val == 0x11: # ascii device control 1:
            stdout.write("\033[2J\033[H")
        else:
            stdout.write(chr(val))
            
        stdout.flush()