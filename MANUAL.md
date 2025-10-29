# Ozpex 64 Manual

This guide explains how to set up the Ozpex 64 emulator, run software on it, and develop your own programs.

## System Overview

The Ozpex 64 is a fictional computer based on the 6502 microprocessor. It includes:

- 32 KB of RAM for user programs
- 16 KB of ROM containing built-in system software
- A serial port for input and output
- A hardware timer for precise timing
- Two 8 KB cartridge slots for external programs, expansions, or user data

## Initial Setup

Install and try Ozpex 64 like this:
```sh
$ git clone https://github.com/BeauConstrictor/Ozpex-64
$ cd ozpex-64
$ python main.py
```

You should see a welcome message and a prompt, indicating that the computer has booted, and the included monitor is running.

## The Monitor

The monitor is a program built into rom that runs automatically on boot. It allows you to efficiently inspect memory, test hardware and write and run programs.

When started, the monitor will begin at an random memory address. Use the `@` key to move to a specific one. After pressing `@` followed by a 4-digit hex memory address, you can start type byte values, which will be written sequentially into memory, starting from that address.

Special keys and commands:

- Read:  Type `>` followed by two addresses to display the contents of that range (inclusive).
- Execute: Typing an `x` will immediately transfer program execution to the current address. Programs can return with either `rts` or `jmp $fff8`.
- Comment: A `;` enters comment mode. Characters typed afterward are ignored until enter is pressed.

## Cartridges

Before you can use this command, you will need actually insert something into a cartridge slot, which you can do like this:

```sh
$ python main.py -1 rom:calc
```

This command will start the emulator with the Calculator program in cartridge slot 1 - usually, programs are designed for cartridge slot 1 and data that they operate on goes in slot 2. This computer has no concept of a filesystem, so a separate cartridge is needed for each 'file' that you want to work on. If you had a physical version of this computer, you would organise these cartridges physically instead of in software like in a modern computer.

You can also use the `-2` option if you want to load something into the second cartridge slot.

The syntax for this option is as follows:

```
[-x/--slotx] [rom/bbram]:<name>
```

Where x is the slot to put the cartridge in, rom is *read-only memory* (most programs will use rom), bbram is *battery-backed ram* (this type of cartridge is used for your data - think text files, songs, etc.) and the name is the specific cartridge to load. To create a new text file for use with the editor program, you can do this:

```
$ python3 main.py -1 rom:editor -2 bbram:sometext
```

This will start the computer with the editor in cartridge slot 1 and your new text file in slot 2.

## Software

At this point, you know enough to start using some full software on your O64. The emulator comes with a variety of programs for you to try, including one (the assembler) which is designed to help you write your own.

### The Editor

```sh
python3 main.py -1 rom:editor
```

This program is a (very) simple text editor, which you can use keep notes and such. Once you are in the program, all you can do is type characters to add to the end of the file, and backspace to delete the last character you typed. To exit, press ESC which will first save your text to CS2, if you have a BBRAM there. It will reopen that file on startup, if you have it in CS2.

### The Calculator

```sh
python3 main.py -1 rom:calc
```

This program is a simple hexadecimal calculator, supporting just addition and subtraction. You enter a two digit hex number, either a `+` or `-` and a second two digit hex number, and the result will immediately be displayed, before moving onto the second line for you to enter the next calculation. Press ESC to exit and return to the monitor.

### The Assembler

```sh
python3 main.py -1 rom:assembler
```

This program lets you efficiently write hex data into memory, and is designed for writing programs. The programs keeps track of your current memory address, and starts it in $0200. You can enter bytes and they will be written into memory sequentially, starting at this address. At any time, press RET to see your current address. You can press `@` to move to a new address. You can also start a comment (some text which will be ignored, and not written) with `;`, which you can then end with RET.

If you want to learn how to write your own software for the Ozpex 64, see [Easy 6502](https://skilldrick.github.io/easy6502/) - an excellent free, online and interactive eBook. Another good resource is Ben Eater's [video series on building and programming his own 6502 computer](https://www.youtube.com/watch?v=LnzuMJLZRdU&list=PLowKtXNTBypFbtuVMUVXNR0z1mu7dp7eH).

Once you can write 6502 assembly, you're 90% of the way there. Just know that there are two ways to exit from an Ozpex 64 program, the first is to `rts` from the top-level of your program. This is usually the cleanest way to exit, but it is not always possible to exit from the top-level, so instead you can `jmp $fff8` - this address is the 'exit vector' and will re-enter the system monitor, without fully restarting it. You should also take a look at the Hardware section of this manual.

### Miscellaneous

There are also a variety of other, much more basic ROMs which you can try out. Here is a full list:

- `classic-loop`: Outputs 'Hello, world!' in a loop, often the first program people write on BASIC.
- `counter`: Counts up to 9 in an infinite loop.
- `hello-world`: Outputs the text `Hello, world!` and `Goodbye, world!`
- `timer`: Counts up by 1 in hexadecimal every second.

## Hardware

This is the computer's memory map:

```plain
RAM: 0x0000 -> 0x7fff
Timer: 0x8000 + 0x8001
Serial: 0x8002
Slot 1: 0x8003 -> 0xa002
Slot 2: 0xa003 -> 0xc002
ROM: 0xc003 -> 0xffff
```

### Timer

The hardware timer is very simple to interface with and does not emit interrupts, so it must be handled through polling.

Writing (any value) to address `0x8000` (register A) will cause the timer to start, so that reading from the timer (discussed below) will cause it to emit the amount of time elapsed since this start point.

Writing to address `0x8001` (register B) will set the units of the timer. Essentially, the timer will divide the time elapsed (in milliseconds) by this value whenever you read it, allowing you to increase the maximum length of time (up to 4.6 hours) that can fit into 16 bits, at the cost of precision - the timer will wrap if it exceeds this value.

Reading from register B will return the high byte of the time elapsed since the last write to register A. Reading from register A will return the low byte.

### Serial

The UART provides a simple interface to the computer, but, like the timer, does not generate interrupts, so polling must be used to check for keypresses.

Writing to address `0x8002` will cause the byte written to be sent to the terminal. There is no need to flush output, and it will appear immediately on the terminal

Reading to that address will return the last character that was typed, and overwrite this value with nul to prevent duplicate reads (this assumes that the nul character will never be typed manually, as it would have to be ignored, but simplifies reading logic somewhat).

The UART has special handling for ASCII device control 1, which simply clears the screen and returns the cursor to the home position. There is potential for more in the future.
