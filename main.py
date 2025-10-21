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
    
    slot1 = ExpansionSlot(0xc000, 0xc7ff)
    slot2 = ExpansionSlot(0xc800, 0xcfff)

    cpu = Cpu({
        "ram": Ram(0x0000, 0xbffc),
        "timer": Timer(0xbffd, 0xbffe),
        "serial": SerialOutput(0xbfff),
        "slot1": slot1,
        "slot2": slot2,
        "rom": Rom(0xd000, 0xffff),
    })

    with open("rom", "rb") as f:
        program = list(f.read())
    
    cpu.mm_components["rom"].load(program, 0xd000)
    
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