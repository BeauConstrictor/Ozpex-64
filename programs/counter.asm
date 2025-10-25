  .org $8003

SERIAL    = $8002
BACKSPACE =   $08
NEWLINE   =   $0a

INTERVAL  = 15

reset:
  ldx #"0"
loop:
  lda #BACKSPACE
  sta SERIAL
  inx
  cpx #"9"+1
  beq reset
  stx SERIAL
  jsr delay
  
  lda SERIAL
  beq loop
  lda #NEWLINE
  sta SERIAL
  rts

delay:
  ldy #0
_delay_loop:
  cpy #INTERVAL
  beq _delay_done
  iny
  nop ; nop has quite a long delay in my emulator
      ; i will add some hardware timer component soon (future: this is done now)
  jmp _delay_loop
_delay_done:
  rts

done:
  jmp done