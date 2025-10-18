import argparse

from cpu import Cpu

DEBUG = False

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument("filepath")
    
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    
    cpu = Cpu()
    
    with open(args.filepath, "rb") as f:
        program = list(f.read())
    
    cpu.mm_components["ram"].load(program, 0x0000)
    cpu.mm_components["ram"].load([0x00, 0x00], 0xfffc)
    
    cpu.reset()
    
    while True:
        instr = cpu.execute()
        if DEBUG:
            cpu.visualise(instr)
            print(cpu.mm_components["ram"].fetch(0x00ff))
            # input()

if __name__ == "__main__":
    main()