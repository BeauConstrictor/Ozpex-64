# Ozpex 64

The Ozpex 64 is a fictional 8-bit computer based around the 6502 microprocessor, which kickstarted the home-computer revolution of the 70s and 80s. It features 32K of RAM and two 8K cartridge slots for programs and hardware expansions. There is no video output as you interface with the machine over an RS-232 serial connection, and there is no speaker.

## Getting Started

To get started with the Ozpex 64, run these commands:

```sh
$ git clone https://github.com/BeauConstrictor/Ozpex-64
$ cd Ozpex-64
$ python3 main.py
```

This will install Ozpex 64 and start the emulator. You should see a prompt that says 'Welcome to Ozpex 64`, which is a message from the computer's built-in machine monitor. This monitor has a few simple functions: it lets you run programs from the cartridge slots and debug them afterward by inspecting & modifying memory. You can also test hardware so make sure it is functioning correctly by reading and writing to their respective memory addresses.

### Machine Monitor

The monitor included in ROM is quite unusual, but allows you to work quickly once you get used to it. Commands are interpreted as you type, so the first character will immediately start whichever command you choose, which will then accept arguments as you type them and immediately execute once it has recieved enough information.

Spaces can be used anywhere in a command and they will be be ignored, so that they can be used to visually separate arguments.

### Commands

- Read: typing an `r` followed by a 2 byte memory address (in hex) will output the value at that address in both hex and ASCII.

- ASCII: typing an `a` followed by a byte in hex will output which ASCII character that byte represents.

- Write: typing a `w` followed by a 2 byte memory address (also in hex), followed by a 1 byte value will write that value to the memory location.

- Jump: typing a `j` followed by a 2 byte memory address (in hex) will start executing a program at that address.

- Clear: typing a `c` will immediately clear the screen.


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

## Emulator

The emulator is a work in progress that develops alongside the software for the computer, so is not yet a complete 6502 emulator. Nevertheless, you can use it to try out the computer by typing `python3 main.py` in the terminal. This will start the computer with both cartridge slots empty. The emulator uses your terminal window as the serial output for programs.

### Syntax

The most common options you will use with the emulator are `-1` and `-2`, which allow you to specify what goes in cartridge slots 1 & 2, respectively. The emulator currently supports two types of cartridge: `rom`, which will load from `roms/<file>.bin` and `bbram` (battery-backed ram, a form of persistent storage), which will load from `bbrams/<file>.bin`. The syntax is as follows:

```plain
python3 main.py [-x|--slotx] [rom|bbram]:<file>
```

When starting the emulator, you can also pass the `--debug` option to watch the computer run at the instruction level. You will probably also want to pass `--rom` followed by a custom program that doesn't depend on input or output to the serial in this case, as the built-in monitor will conflict with the debug output.

Check <instructions.md> for more detailed information on the progress of the emulator itself.

## Writing Software

If you, for whatever reason, want to write a program for the Ozpex 64, then take a look at some of the included programs in `/programs`.

The simplest program for the Ozpex 64 looks like this:

```asm
SERIAL = $8002 ; this is the address of the computer's serial output.

  .org $8003   ; tells the assembler where this program will go in memory.
               ; $8003 refers to the start of cartridge slot 1.

  lda #"A"     ; load an ASCII 'A' into the A register.
  sta S        ; write the contents of the A register to the serial port.

  rts          ; return back to the system monitor after the
               ; program has finished executing.
```

This program simply outputs an uppercase `A` to the output. If you put this file in `/programs` and run `./build.sh`, the program will compile so that you can run it like this:

```sh
$ python3 main.py -1 rom:myprog
Welcome to Ozpex 64 (2025)
Monitor: READY

? j 8003
A
? █
```

For more resources on 6502 programming, see [Easy 6502](https://skilldrick.github.io/easy6502/) - an excellent free, online and interactive eBook. Another good resource is Ben Eater's [video series on building and programming his own 6502 computer](https://www.youtube.com/watch?v=LnzuMJLZRdU&list=PLowKtXNTBypFbtuVMUVXNR0z1mu7dp7eH).

## Contributing

Please do not make pull requests, as I am working on this project mainly to improve my own knowledge as a programmer on how computers really work, but feel free to fork my repo and do whatever you like with it.
