# Ozpex 64

A fictional 8-bit retro home-computer built for tinkerers, as your first step into the world of (truly) low-level development.

![GNU GPL v2.0 License](https://img.shields.io/github/license/BeauConstrictor/ozpex-64?style=flat)

This project is broken up into 3 main parts: the emulator, the Logisim implementation and the included software. All three of these are made to be compatible with the design for a fictional computer that *could* have existed around the late '70s/early '80s, but never did.

## The Emulator

Before proceeding, ensure that you have [`cool-retro-term`](https://github.com/Swordfish90/cool-retro-term) installed and in your system `PATH`.

To start the emulator, navigate to the root of this repository (after cloning it) and run this command:

```
$ python3 main.py --gui
```

This will start the emulator in GUI mode, which allows you to more easily manage your *machines*. Machines are files containing the configuration of your Ozpex 64 so that you can quickly load up the same ROM and cartridges. In the sidebar on the left, you will see two example machines that are included with the GUI. Pong is a demake of the original Atari Pong that demonstrates the capabilities of the Ozpex 64 in ~300 lines of assembly. To try out the Pong machine, select its entry in the machine list on the left, and hit the start button at the bottom right of the window.

## The Logisim Implementation

The Ozpex 64 has been implemented in the free digital logic design software [Logisim Evolution](https://github.com/logisim-evolution/logisim-evolution). You can find this in the `logisim/` directory of this repo. Once you have opened the `.circ` file in Logisim Evolution, you can set the clock speed to whatever you desire and start the simulation. There are some cartridges included which you can easily insert. The ROM is prepopulated with the monitor program.

## The Software

This repository also includes some simple software that you can run either in-emulator or from Logisim. You can find pre-built binaries of these programs in the `roms/` directory and the corresponding assembly source files in the `programs/` directory.

For more complex software to try, or to read through and learn from (although I can't vouch for my assembly skills), see [Ozpex-DOS](https://github.com/BeauConstrictor/Ozpex-DOS). This is a complete disk-operating-system for the computer that will eventually have a complete development workflow so that you can develop full software right on the machine.