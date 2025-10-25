  .org $8003

TIMER =      $8000
SERIAL =     $8002

BACKSPACE =  $08
NEWLINE =    $0a

; memory allocation:
LAST_TIMER = $50        ; 1 byte

main:
  ; tell the timer to output in units of 4ms. only the high byte is checked so
  ; this measures in 1024ms, close enough to 1s
  lda #4;ms
  sta TIMER+1

  ; write any value to start the timer
  sta TIMER

timer:
  ; only output if the timer has changed
  lda TIMER+1
  cmp LAST_TIMER
  beq timer
  sta LAST_TIMER

  ; output the timer
  jsr print

  ; check the timer again
  jmp timer

; undo the last print & output the a register
print:
  ldx #BACKSPACE
  stx SERIAL
  stx SERIAL

  jsr hex_byte
  cpx #"0"
  beq skip_high_byte
  stx SERIAL
skip_high_byte:
  sty SERIAL

  rts

; return (in a) the a register as hex
; modifies: a (duh)
hex_nibble:
  cmp #10
  bcc _hex_nibble_digit
  clc
  adc #"a" - 10
  rts
_hex_nibble_digit:
  adc #"0"
  rts

; return (in x & y) the a register as hex
; modifies: x, y, a
hex_byte:
  pha ; save the full value for later
  ; get just the MSN
  lsr
  lsr
  lsr
  lsr
  jsr hex_nibble
  tax ; but the hex char for the MSN in x

  pla ; bring back the full value
  and #$0f ; get just the LSN
  jsr hex_nibble
  tay ; but the hex char for the LSN in y

  rts