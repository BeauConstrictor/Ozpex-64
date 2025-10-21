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

- [x] ADC
- [ ] AND
- [ ] ASL
- [ ] BCC
- [ ] BCS
- [x] BEQ
- [ ] BIT
- [ ] BMI
- [x] BNE
- [ ] BPL
- [ ] BRK
- [ ] BVC
- [ ] BVS
- [x] CLC
- [x] CLD
- [x] CLI
- [x] CLV
- [x] CMP
- [x] CPX
- [x] CPY
- [ ] DEC
- [ ] DEX
- [ ] DEY
- [ ] EOR
- [x] INC
- [x] INX
- [x] INY
- [x] JMP
- [x] JSR
- [x] LDA
- [x] LDX
- [x] LDY
- [ ] LSR
- [x] NOP
- [ ] ORA
- [ ] PHA
- [ ] PHP
- [ ] PLA
- [ ] PLP
- [ ] ROL
- [ ] ROR
- [ ] RTI
- [x] RTS
- [x] SBC
- [x] SEC
- [x] SED
- [x] SEI
- [x] STA
- [x] STX
- [x] STY
- [ ] TAX
- [ ] TAY
- [ ] TSX
- [ ] TXA
- [ ] TXS
- [ ] TYA
