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
- [ ] Relative
- [x] Absolute
- [x] Absolute,X
- [x] Absolute,Y
- [x] Indirect
- [x] Indexed Indirect
- [x] Indirect Indexed

## Instructions

This is a list of the instructions that I have completed, and the ones that I have left to complete.

- [ ] ADC
- [ ] AND
- [ ] ASL
- [ ] BCC
- [ ] BCS
- [ ] BEQ
- [ ] BIT
- [ ] BMI
- [ ] BNE
- [ ] BPL
- [ ] BRK
- [ ] BVC
- [ ] BVS
- [ ] CLC
- [ ] CLD
- [ ] CLI
- [ ] CLV
- [ ] CMP
- [ ] CPX
- [ ] CPY
- [ ] DEC
- [ ] DEX
- [ ] DEY
- [ ] EOR
- [x] INC
- [x] INX
- [x] INY
- [x] JMP
- [ ] JSR
- [x] LDA
- [x] LDX
- [x] LDY
- [ ] LSR
- [ ] NOP
- [ ] ORA
- [ ] PHA
- [ ] PHP
- [ ] PLA
- [ ] PLP
- [ ] ROL
- [ ] ROR
- [ ] RTI
- [ ] RTS
- [ ] SBC
- [ ] SEC
- [ ] SED
- [ ] SEI
- [x] STA
- [x] STX
- [x] STY
- [ ] TAX
- [ ] TAY
- [ ] TSX
- [ ] TXA
- [ ] TXS
- [ ] TYA
