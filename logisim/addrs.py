def main() -> None:
    data = bytearray(65536)
    
    for i in range(65536):
        is_in = 1 if 0xa003 <= i <= 0xc002 else 0
        data[i] = is_in
    
    with open("cs2-addrs.bin", "wb") as f:
        f.write(data)
    
if __name__ == "__main__":
    main()