import os.path
import argparse
from sys import stderr
from time import sleep
from typing import Iterator

from components.cpu import Cpu
from components.ram import Ram
from components.rom import Rom
from components.timer import Timer
from components.serial import SerialOutput
from components.expansion_slot import ExpansionSlot
from components.mm_component import MemoryMappedComponent
from components.expansion_slot import RomExpansion, BbRamExpansion

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ozpex-64",
        description = "A fictional 8-bit computer and emulator based on the "
                      "6502",
    )
                         
    parser.add_argument("-1", "--slot1")
    parser.add_argument("-2", "--slot2")
    
    parser.add_argument("-r", "--rom",
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "roms", "monitor.bin"),
                        help="overwrite the default monitor rom")
    
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="watch the emulator execute individual instructions")
    
    parser.add_argument("-n", "--nocrash",
                        action="store_true",
                        help="disable crashes on unknown opcodes")
    
    parser.add_argument("-g", "--gui",
                        action="store_true",
                        help="start the ozpex 64 gui (ignores other arguments)")
    
    return parser.parse_args()

def load_slot(literal: str, slot: ExpansionSlot) -> None:
    parts = literal.split(":")
    expansion = parts[0]
    if len(parts) > 1: arg = ":".join(parts[1:])
    else: arg = None
    
    expansions = {
        "rom":   RomExpansion,
        "bbram": BbRamExpansion,
    }
    
    if expansions.get(expansion, None) is None:
        print("\n\n\033[31m", end="")
        print(f"6502: unknown expansion card: '{expansion}'.",
              "\033[0m", file=stderr)
        exit(1)
    
    e = expansions[expansion](arg)
    slot.mount(e.read, e.write)

def create_machine(rom: str, slot1: str|None, slot2: str|None,
                   serial: MemoryMappedComponent) -> Cpu:
    # MEMORY MAP:
    # ram:    $0000 -> $7fff  (32,768 B)
    # timer:  $8000 && $8001
    # serial: $8002
    # slot 1: $8003 -> $a002  ( 8,192 B)
    # slot 2: $a003 -> $c002  ( 8,192 B)
    # rom:    $c003 -> $ffff  (16,381 B) - an odd size, but it's just whatever
    #                                      fit in the remaining space
    
    cpu = Cpu({
        "ram": Ram(0x0000, 0x7fff),
        "timer": Timer(0x8000, 0x8001),
        "serial": serial(0x8002),
        "slot1": ExpansionSlot(0x8003, 0xa002),
        "slot2": ExpansionSlot(0xa003, 0xc002),
        "rom": Rom(0xc003, 0xffff),
    })

    with open(rom, "rb") as f:
        rom_data = list(f.read())
    cpu.mm_components["rom"].load(rom_data, 0xc003)
        
    if slot1: load_slot(slot1, cpu.mm_components["slot1"])
    if slot2: load_slot(slot2, cpu.mm_components["slot2"])
    
    cpu.reset()
    
    return cpu

def simulate(cpu: Cpu, nocrash: bool, debug: bool) -> Iterator[None]:
    cycles_executed = 0
    
    while True:
        try:
            instr = cpu.execute()
            yield
                       
        except NotImplementedError as e:    
            if nocrash: continue
            print("\n\n\033[31m", end="")
            print(f"6502: {e}, execution aborted.", end="")
            print("\033[0m")
            exit(1)
        if debug:
            cpu.visualise(instr)
            input()

def main() -> None:
    args = parse_args()
    
    if args.gui:
        import gui.main
        gui.main.App().mainloop()
        return
    
    cpu = create_machine(args.rom, args.slot1, args.slot2, SerialOutput)
    
    cycle = 0
    for _ in simulate(cpu, args.nocrash, args.debug):
        # on my computer, this gets ~1MHz
        if cycle % 200 == 0:
            cycle = 0
            sleep(0.000001)
        cycle += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[31m", end="")
        print(f"emu: ctrl+c exit.", end="")
        print("\033[0m")
        exit(0)