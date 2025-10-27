import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument("filename")
    parser.add_argument("-o", "--out", default="a.out")
    parser.add_argument("-s", "--start", default=0x8003, type=int)
    
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    
    with open(args.filename, "rb") as f:
        data = f.read()

    with open(args.out, "wb") as f:
        f.write(b'\x00' * 0x8003)
        f.write(data)

if __name__ == "__main__":
    main()