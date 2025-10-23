# Ozpex 64

The Ozpex 64 is a fictional 8-bit computer & emulator based on the 6502
microprocessor. It has 32K of RAM, 16K or ROM and two cartridge slots. There is no graphics support, as all output goes to a serial terminal. Finally, there is also a hardware timer for precision as the included emulator is not 'cycle-accurate' and has no concept of how long an instruction should take to execute.

## Monitor

This computer features a custom machine monitor to test out hardware and run a program from one of the cartridge slots.

This monitor is very unusal as commands are interpreted as they are typed, so there is no need to press enter once you are done, as the command knows when it has enough arguments and will automatically execute. This does mean that if you make a typing mistake you have to commit to it and finish the command - there is no way to correct the typo.

### Commands

Commands are made up of 1 character, and spaces anywhere in the command are ignored so that you can use them for clarity, or leave them out if you need to work faster.

- read (`r`): typing an `r` followed by a 2 byte memory address (in hex) will output the value at that address in both hex and ASCII.

- write (`w`): typing a `w` followed by a 2 byte memory address (also in hex), followed by a 1 byte value will write that value to the memory location.

- jump (`j`): typing a `j` followed by a 2 byte memory address (in hex) will start executing code at that address.

- execute (`x`): a shorthand for jump, typing an `x` followed by either a 1, 2 or 3 will jump to cartridge slot 1, slot 2 and the ROM respectively.

- clear (`c`): typing a `c` will immediately clear the screen.

## Emulator

The emulator is a work in progress that develops alongside the software for the computer, so is not yet a complete 6502 emulator. Nevertheless, you can use it to try out the computer by typing `./run monitor` in the terminal. This will assemble the built-in monitor and load it into ROM before starting the computer. The emulator uses your terminal window as the serial output for programs.

Check <instructions.md> for more detailed information on the completion of the emulator itself.

## Contributions

Please do not make pull requests, as I am working on this project to improve my own knowledge as a programmer on how computers really work, but feel free to fork my repo and do whatever you like with it.
