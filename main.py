import argparse

from components.cpu import Cpu
from components.ram import Ram
from components.rom import Rom
from components.timer import Timer
from components.serial import SerialOutput
from components.expansion_slot import ExpansionSlot

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--debug",
                        action="store_true")
    
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    
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
        "serial": SerialOutput(0x8002),
        "slot1": ExpansionSlot(0x8003, 0xa002),
        "slot2": ExpansionSlot(0xa003, 0xc002),
        "rom": Rom(0xc003, 0xffff),
    })

    with open("rom", "rb") as f:
        rom = list(f.read())
    cpu.mm_components["rom"].load(rom, 0xc003)
    
    with open("slot1", "rb") as f:
        slot1_data = list(f.read())
    cpu.mm_components["slot1"].mount(lambda a: slot1_data[a], None)
    
    cpu.reset()
    
    while True:
        try:
            instr = cpu.execute()
        except NotImplementedError as e:    
            print("\n\n\033[31m", end="")
            print(f"6502: {e}, execution aborted.", end="")
            print("\033[0m")
            exit(1)
        if args.debug:
            cpu.visualise(instr)
            input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[31m", end="")
        print(f"6502: ctrl+c: exit.", end="")
        print("\033[0m")
        exit(0)