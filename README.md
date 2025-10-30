# Ozpex 64

The Ozpex 64 is a fictional 8-bit computer based around the 6502 microprocessor, which kickstarted the home-computer revolution of the 70s and 80s. It features 32K of RAM and two 8K cartridge slots for programs and hardware expansions. There is no video output as you interface with the machine over an RS-232 serial connection, and there is no speaker.

## Getting Started

To get started with the Ozpex 64, run these commands:

```sh
$ git clone https://github.com/BeauConstrictor/Ozpex-64
$ cd Ozpex-64
$ python3 main.py
```

This will install Ozpex 64 and start the emulator. You should see a prompt that says 'Ozpex 64`, which is a message from the computer's built-in machine monitor. This monitor has a few simple functions: it lets you run programs, test hardware, check memory and write programs of your own in raw machine code.

Read the <MANUAL.md> to go further.

### Machine Monitor

Included in ROM, and started on boot is the hex monitor for the Ozpex 64, reminiscient of [WozMon, from the Apple I](https://www.sbprojects.net/projects/apple1/wozmon.php). It allows you to efficiently read and write to the computer's memory and run programs.

## Emulator

The emulator is a work in progress that develops alongside the software for the computer, so is not yet a complete 6502 emulator. Nevertheless, you can use it to try out the computer by typing `python3 main.py` in the terminal. This will start the computer with both cartridge slots empty. The emulator uses your terminal window as the serial output for programs.

## Logisim Implementation

The computer has also been implemented in Logisim Evolution, using a [premade 6502 core](https://github.com/solrabizna/logi6502). The computer is almost fully functional, but is still missing the hardware timer. The pong game (and most future games) will not look great, as the serial terminal does not support clearing the screen using the Ozpex 64-specific clearing system (0x11). Despite this, you can still use the computer, and everything else will function correctly. You can even run the simulator faster my custom emulator on my machine. There is also a tool included that converts ROM files into the correct format to load directly onto cartridges in Logisim.

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
 O64 Monitor v1.0.0
Welcome to Ozpex 64!

? █
```

For more resources on 6502 programming, see [Easy 6502](https://skilldrick.github.io/easy6502/) - an excellent free, online and interactive eBook. Another good resource is Ben Eater's [video series on building and programming his own 6502 computer](https://www.youtube.com/watch?v=LnzuMJLZRdU&list=PLowKtXNTBypFbtuVMUVXNR0z1mu7dp7eH).

## Contributing

Please do not make pull requests, as I am working on this project mainly to improve my own knowledge as a programmer on how computers really work, but feel free to fork my repo and do whatever you like with it.

## Todos

- [ ] At some point, implement a syscall mechanism using the `brk` instruction so that I'm not copy-pasting hex display rountines everywhere.
