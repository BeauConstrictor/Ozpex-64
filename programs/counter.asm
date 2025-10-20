  .org $d000

SERIAL = $ffff
CLEAR =    $11

INTERVAL = 15

reset:
  ldx #"0"
loop:
  lda #CLEAR
  sta SERIAL
  inx
  cpx #"9"+1
  beq reset
  stx SERIAL
  jsr delay
  jmp loop

delay:
  ldy #0
_delay_loop:
  cpy #INTERVAL
  beq _delay_done
  iny
  nop
  jmp _delay_loop
_delay_done:
  rts

done:
  jmp done

; reset vector
  .org  $fffc
  .word reset