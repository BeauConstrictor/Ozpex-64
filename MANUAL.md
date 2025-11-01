# Ozpex 64 Manual

The document provides an in-depth guide on how to set-up and use the Ozpex 64 Emulator and its included software.

## Setup

To install and test the emulator, run these commands:

```
$ git clone https://github.com/BeauConstrictor/Ozpex-64
$ cd Ozpex-64
$ python main.py
```

Once in the emulator, you should automatically be booted into the monitor program, as it is built into ROM. This program gives you a means to interact with the system and, most importantly, start more complex software, which brings me onto:

## The Monitor

The machine monitor is a simple yet powerful tool for managing memory on an Ozpex 64. The program keeps just one piece of state: your current memory address, which is used as an argument by all the operations available, which are:

- Writing: To write to memory, simply type out two hex characters and the byte will immediately be written into memory and your current address will be incremented so that your next write will come immediately after.

- Reading: To read from memory, use a `>` sign and type out a memory address. The monitor will then read and print out the values of every memory address between your current address and the second one you typed.
- Executing: Hitting an `x` will jump to your current address and run it as a subroutine, so the program that you run can return to the monitor using an `rts` instruction. Programs can also return by jumping directly to `$fff8`. To make starting programs easier, you can use the `!` key to quickly start the program in slot 1, and the `"` key to start the program in slot 2.
- Moving: You can move directly to a new address for any of the above operations using the `@` key, followed by a full hex memory address.
- Commenting: If you type a `;`, characters afterward will be completely ignored until you press enter.

## Included Software

The Ozpex 64 repository includes several pieces of included software, two of which have already been mentioned.

- Pong: This is a game for the Ozpex, and uses just the serial port for I/O. It is deterministic, so the game plays out in the same way every time. Move with W & S.
- Calc: This is a simple hex calculator that operates on single bytes, supporting just addition and subtraction.
- Editor: This is a simple text editor that saves to a BBRAM in CS2 on exit. It only supports 256 byte documents, and you cannot move your cursor from the end of the buffer when editing.
- Miscellaneous: There are also some other small programs that predate the monitor itself and just exist for testing various pieces of the emulator. You can find these in the `./programs` directory, but they are quite poorly written, so I wouldn't use them for practice.

## Writing Your Own Software

Using the monitor, you can type your own programs into the machine and run them, but this isn't exactly an ideal development environment. There are 2 other ways to develop software targeting the Ozpex 64.

### The Assembler

The Assembler makes it easier to enter programs into an Ozpex 64 by using instruction mnemonics. To use the assembler, put it in cartridge slot 1:

```
$ python main.py -1 rom:assembler
```

You can then enter mnemonic mode with the `!` key (you can leave the assembler again with escape). The assembler behaves similarly to the monitor, but with a few key differences:

- Input is buffered, so nothing actually happens until you press enter, unlike in the monitor. This makes it easier to correct mistakes.
- You cannot read or execute memory in the assembler, so you must hit ESC, perform the operation, and then use `!` to re-enter the assembler.

If you are happy with your program, you can write it to a BBRAM (a cartridge that you can write to) and load it whenever. This command will put a BBRAM in CS2:

```
$ python main.py -1 rom:assembler -2 bbram:myprog
```

You can then jump to CS2 in the assembler like this:

```
(mnemonic mode)
9185: @a003

a003: ; you can start writing code here
```

### External Environment

Most software for the Ozpex 64 is not developed on the computer itself. It is written in an assembly file in the `./programs` directory of this repository and built using `./build.sh`. This will automatically assemble the file into a format that can be loaded as a cartridge. The script will also put a file in `./apis` that contains the memory addresses for all the subroutines and variables in the program, so that you can debug from the monitor.

This setup will require you to have [vasm](http://compilers.de/vasm.html) installed on your computer, and have somewhere to edit plain text documents.

### Writing 6502 Assembly

Any programs you write for the Ozpex 64 will have to be written in assembly. This can sound daunting, but learning assembly can be incredibly rewarding and is that primary reason that the Ozpex 64 exists. Assembly is quite a departure from other programming languages, including languages like C which are usually considered very low-level. It is like this simply because assembly is the most accurate representation of what *exactly* your CPU is doing when it runs code (that you can reasonably write complex software with). This language is more precisely known as *6502 assembly* and you can find many guides online, such the interactive guide [Easy 6502](https://skilldrick.github.io/easy6502/), or [Ben Eater's video series](https://www.youtube.com/watch?v=LnzuMJLZRdU&list=PLowKtXNTBypFbtuVMUVXNR0z1mu7dp7eH) where he builds his own computer based on the 6502.

None of these guides however are specifically compatible with the Ozpex 64, but once you have learnt the basics of 6502 assembly, it is not a big leap to go to writing full programs for this machine - you just need to know how to interface with the hardware using memory mapped I/O. Here is everything you need to know:

## Hardware

This is the computer's memory map:

```
RAM: 0x0000 -> 0x7fff
Timer: 0x8000 + 0x8001
Serial: 0x8002
Slot 1: 0x8003 -> 0xa002
Slot 2: 0xa003 -> 0xc002
ROM: 0xc003 -> 0xffff
```

### Timer

The computer features a simple hardware timer to help you measure precise time intervals, as the computer does not run at a set clock speed, so games would be very inconsistent without one. It is very simple to interface with and does not emit interrupts, so you must use polling to measure time.

Writing (any value) to address 0x8000 (register A on the timer) will cause the timer to start, so that reading from the timer (discussed below) will cause it to emit the amount of time elapsed since this start point.

Writing to address 0x8001 (register B) will set the units of the timer. Essentially, the timer will divide the time elapsed (in milliseconds) by this value whenever you read it, allowing you to increase the maximum length of time (up to 4.6 hours) that can fit into 16 bits, at the cost of precision - the timer will wrap if it exceeds this value.

Reading from register B will return the high byte of the time elapsed since the last write to register A. Reading from register A will return the low byte.

#### Serial

The Ozpex 64 does not feature a video display of any kind, to make simple programs easier to write, instead you use a serial port that outputs to a text terminal.

The UART (serial port) like the timer, does not generate interrupts, so polling must be used to check for keypresses.

Writing to address 0x8002 will cause the byte written to be sent directly to the terminal. There is no need to flush output, and it will appear immediately on the terminal.

Reading to that address will return the last character that was typed, and overwrite this value with null ($00) to prevent duplicate reads, which allows you to simply `bne` to check if a key has been pressed.