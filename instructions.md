# Progress

## Addressing Modes

This is a list of the addressing modes that I have completed, and the ones that
I have left to complete.

- [x] Implicit (represented as `None`)
- [x] Accumulator

For the accumulator addressing mode, because the fetch functions do not
explicitly take a `byte`, but an `int` (Python has no `byte` type), I created a
special memory address outside of the normal addressing range so that nothing
can interfere with it: `-0xacc`. This address will be returned by
`addr_accumulator` and when fetched or written to by the cpu, the accumulator
itself will be accessed.

- [x] Immediate
- [x] Zero Page
- [x] Zero Page,X
- [x] Zero Page,Y
- [x] Relative
- [x] Absolute
- [x] Absolute,X
- [x] Absolute,Y
- [x] Indirect
- [x] Indexed Indirect
- [x] Indirect Indexed

## Instructions

This is a list of the instructions that I have completed, and the ones that I have left to complete.

  Emu Asm
- [x] [ ] ADC
- [ ] [ ] AND
- [x] [ ] ASL
- [x] [ ] BCC
- [x] [ ] BCS
- [x] [ ] BEQ
- [ ] [ ] BIT
- [ ] [ ] BMI
- [x] [ ] BNE
- [ ] [ ] BPL
- [ ] [-] BRK
- [ ] [ ] BVC
- [ ] [ ] BVS
- [x] [ ] CLC
- [x] [-] CLD
- [x] [-] CLI
- [x] [ ] CLV
- [x] [ ] CMP
- [x] [ ] CPX
- [x] [ ] CPY
- [ ] [ ] DEC
- [ ] [ ] DEX
- [ ] [ ] DEY
- [ ] [ ] EOR
- [x] [ ] INC
- [x] [ ] INX
- [x] [ ] INY
- [x] [ ] JMP
- [x] [x] JSR
- [x] [x] LDA
- [x] [x] LDX
- [x] [x] LDY
- [x] [ ] LSR
- [x] [ ] NOP
- [ ] [ ] ORA
- [x] [ ] PHA
- [ ] [ ] PHP
- [x] [ ] PLA
- [ ] [ ] PLP
- [ ] [ ] ROL
- [ ] [ ] ROR
- [ ] [-] RTI
- [x] [x] RTS
- [x] [ ] SBC
- [x] [ ] SEC
- [x] [-] SED
- [x] [-] SEI
- [x] [x] STA
- [x] [x] STX
- [x] [x] STY
- [x] [ ] TAX
- [x] [ ] TAY
- [x] [ ] TSX
- [x] [ ] TXA
- [x] [ ] TXS
- [x] [ ] TYA
