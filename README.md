# Ozpex 64

The Ozpex 64 is a fictional 6502-based to experience what programming was like for developers in the 1980s. It is a simple system to develop for, while avoiding unnecessary abstractions. If you want to learn how computers work on a low level, the Ozpex 64 is simple enough to wrap your head around in an afternoon, but is complex enough to warrant experimentation.

## System Details

- 32K of RAM from 0x0000 -> 0x7fff
- Hardware Timer at 0x8000 & 0x8001
- Serial I/O at 0x8002
- 8K Cartridge / Hardware Expansion Slot at 0x8003 -> 0xa002
- 8K Cartridge / Hardware Expansion Slot at 0xa003 -> 0xc002
- ~16K ROM at 0xc003 -> 0xffff

## How to Try it

The easiest way to try the Ozpex 64 is through emulation. This repository includes an custom emulator for the system that lets you easily build and run custom software, and includes a monitor program in ROM that helps you experiment directly on the machine.

You can also try out Ozpex software in Logisim Evolution, as the Ozpex 64 has been implemented in Logisim using [SolraBizna's 6502 core](github.com/SolraBizna/logi6502).

## Writing Software

The Ozpex 64 is designed for you to write your own software, and there are a few ways to do it. To get started, you can try the included assembler like this:

```
$ python main.py -1 rom:assembler
```

This command will start the emulator with the assembler program in cartridge slot 1. On startup, you will not see the assembler, but the monitor - the program built into ROM. To start the assembler, press `!`. This will immediately start the assembler, and you should see a message like this:

```
(mnemonic mode)
d4e2: 
```

The memory address you start at is unpredictable, so you can move to a specfic address with the `@` sign. Usually, you will want to move to $0300, as this address is out of the way of RAM that is used my software (the zero page goes in `$00xx`, the stack goes in `$01xx` and the input buffer usually goes in `$02xx`). If you want to save your program, you can go put a BBRAM in cartridge slot 2, and go to address `$a003`, to write code directly into the cartridge. To mount a BBRAM, use this command:

```
$ python main.py 1 rom:assembler -2 bbram:myprograms
```

When you are in the mnemonic mode, you can type out assembly instructions and have them immediately written into memory upon hitting enter. While you can write programs this way, there is no support for labels, so must programs you write will simply be scripts that wrap subroutines included in ROM. In order to write more complex programs, you will want to assemble them using a modern tool such as [vasm](http://www.compilers.de/vasm.html). This repository includes a build script that will automatically assemble all programs in the `./programs` directory, and put the output in `./roms`, so that you can easily load your program as a cartridge. Also, an 'api' fill will be saved into the `./apis` directory, containing addresses of subroutines and variables used by the program.
