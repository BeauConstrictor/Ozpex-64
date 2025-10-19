import argparse

from components.cpu import Cpu
from components.ram import Ram
from components.rom import Rom
from components.serial import SerialOutput
from components.expansion_slot import ExpansionSlot

RESETVEC = 0xfffc

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--debug",
                        action="store_true")
    
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    
    slot1 = ExpansionSlot(0xc000, 0xc7ff)
    text = [ord(c) for c in "Hello, world!"]
    slot1.mount(lambda addr: text[addr] if 0 <= addr < len(text) else 0x00,
                lambda addr, val: None)

    slot2 = ExpansionSlot(0xc800, 0xcfff)

    cpu = Cpu({
        "ram": Ram(0x0000, 0xbfff),
        "slot1": slot1,
        "slot2": slot2,
        "rom": Rom(0xd000, 0xfffe),
        "serial": SerialOutput(0xffff),
    })


    with open("rom", "rb") as f:
        program = list(f.read())
    
    cpu.mm_components["rom"].load(program, 0xd000)
    
    cpu.reset()
    
    while True:
        instr = cpu.execute()
        if args.debug:
            cpu.visualise(instr)
            print(cpu.mm_components["ram"].fetch(0x00ff))
            input()

if __name__ == "__main__":
    main()