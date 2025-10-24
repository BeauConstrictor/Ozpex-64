# Ozpex 64

The Ozpex 64 is a fictional 8-bit computer & emulator based on the 6502
microprocessor. It has 32K of RAM, 16K or ROM and two cartridge slots. There is no graphics support, as all output goes to a serial terminal. Finally, there is also a hardware timer for precision as the included emulator is not 'cycle-accurate' and has no concept of how long an instruction should take to execute.

## Monitor

This computer features a custom machine monitor to test out hardware and run a program from one of the cartridge slots.

This monitor is very unusual as commands are interpreted as they are typed, so there is no need to press enter once you are done, as the command knows when it has enough arguments and will automatically execute. This does mean that if you make a typing mistake you have to commit to it and finish the command - there is no way to correct the typo.

### Commands

Commands are made up of 1 character, and spaces anywhere in the command are ignored so that you can use them for clarity, or leave them out if you want to work faster.

- read (`r`): typing an `r` followed by a 2 byte memory address (in hex) will output the value at that address in both hex and ASCII.

- write (`w`): typing a `w` followed by a 2 byte memory address (also in hex), followed by a 1 byte value will write that value to the memory location.

- jump (`j`): typing a `j` followed by a 2 byte memory address (in hex) will start a program at that address.

- clear (`c`): typing a `c` will immediately clear the screen.

## Emulator

The emulator is a work in progress that develops alongside the software for the computer, so is not yet a complete 6502 emulator. Nevertheless, you can use it to try out the computer by typing `./run editor` in the terminal. This will assemble the built-in monitor, load it into ROM, assemble the text editor and load it into slot 1, and then start the computer. The emulator uses your terminal window as the serial output for programs.

Check <instructions.md> for more detailed information on the completion of the emulator itself.

## Memory Map

This is the computer's memory map, with address ranges (`->`) inclusive.

- RAM:    `0x0000` -> `0x7fff`
- Timer:  `0x8000` + `0x8001`
- Serial: `0x8002`
- Slot 1: `0x8003` -> `0xa002`
- Slot 2: `0xa003` -> `0xc002`
- ROM:    `0xc003` -> `0xffff`

### Timer

The hardware timer is very simple to interface with and does not emit interrupts, so it must be handled through polling.

Writing (any value) to address `0x8000` (register A) will cause the timer to start, so that reading from the timer (discussed below) will cause it to emit the amount of time elapsed since this start point.

Writing to address `0x8001` (register B) will set the units of the timer. Essentially, the timer will divide the time elapsed (in milliseconds) by this value whenever you read it, allowing you to increase the maximum length of time (up to 4.6 hours) that can fit into 16 bits, at the cost of precision - the timer will wrap if it exceeds this value.

Reading from register B will return the high byte of the time elapsed since the last write to register A. Reading from register A will return the low byte.

### Serial

The UART provides a simple interface to the computer, but, like the timer, does not generate interrupts, so polling must be used to check for keypresses.

Writing to address `0x8002` will cause the byte written to be sent to the terminal. There is no need to flush output, and it will appear immediately on the terminal

Reading to that address will return the last character that was typed, and overwrite this value with `nul` to prevent duplicate reads (this assumes that the `nul` character will never be typed manually, as it would have to be ignored, but simplifies reading logic somewhat).

The UART has special handling for ASCII device control 1, which simply clears the screen and returns the cursor to the home position. There is potential for more in the future.

## Writing Software

If you want to write software for this computer (for some reason), take a look at some of the example programs in `./programs`. Programs should typically go in slot 1 (slot 2 is for extra hardware or persistent storage), although this is not an enforced rule. This means programs will be mounted at `0x8003`, so make sure your assembly mentions that.

Your program should include some facility to exit, which can `rts` (at the top level of your program) to return to the machine monitor.

## Contributions

Please do not make pull requests, as I am working on this project to improve my own knowledge as a programmer on how computers really work, but feel free to fork my repo and do whatever you like with it.
