  .org $d000


SERIAL = $ffff

reset:
  ldx #0
loop:
  lda message,x
  beq done
  sta SERIAL
  inx
  jmp loop
  
done:
  jmp done

message:
  .byte "Hello, world!", 0


; reset vector
  .org  $fffc
  .word reset
