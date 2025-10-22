  .org $c003

TIMER =      $8000
SERIAL =     $8002

CLEAR =      $11
NEWLINE =    $a

PRINT_INTERVAL = 250;ms

; memory allocation:
LAST_TIMER =  $50        ; 1 byte

reset:
    lda #PRINT_INTERVAL
    sta TIMER+1

    sta TIMER ; start timer

timer:
    ldy TIMER
    cpy LAST_TIMER
    beq timer

    jsr print
    sty LAST_TIMER
    jmp timer

print:
  ldx #0
_print_loop:
  lda message,x
  beq _print_done
  sta SERIAL
  inx
  jmp _print_loop
_print_done:
  rts

message:
  .byte "HELLO WORLD", NEWLINE, 0

; reset vector
  .org  $fffc
  .word reset