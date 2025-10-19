from abc import ABC, abstractmethod

class MemoryMappedComponent(ABC):
    @abstractmethod
    def contains(self, addr: int) -> bool: ...
    
    def fetch(self, addr: int) -> int: return 0
    def write(self, addr: int, val: int) -> None: pass