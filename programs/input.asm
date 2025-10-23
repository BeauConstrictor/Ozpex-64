  .org $c003

SERIAL = $8002

reset:
  ; wait in a loop for a key to be pressed and put it in a
  lda SERIAL
  beq reset

  ; echo the char that was typed
  sta SERIAL

  ; go back and wait for the next key
  jmp reset

; reset vector
  .org  $fffc
  .word reset
