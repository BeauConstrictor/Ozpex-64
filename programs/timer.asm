  .org $c003

TIMER =      $8000
SERIAL =     $8002

CLEAR =      $11
NEWLINE =    $a

; memory allocation:
LAST_TIMER = $50        ; 1 byte

reset:
    lda #4 ; 4ms per time unit. only high byte is checked so this becomes 1s
           ; per time unit.
    sta TIMER+1

    sta TIMER ; start timer

    lda #$00
    sta LAST_TIMER ; make sure that it prints the first time around
    lda #CLEAR
    sta SERIAL

timer:
    ldy TIMER+1
    cpy LAST_TIMER
    beq timer

    jsr print
    sty LAST_TIMER
    jmp timer

print:
    ; clear the screen and print the current timer from the y reg
    lda #CLEAR
    sta SERIAL
    tya
    adc #"0" - 2
    sta SERIAL
    rts

; reset vector
  .org  $fffc
  .word reset