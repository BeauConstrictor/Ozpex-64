  .org $c003

SERIAL  = $8002
CS1 = $8003
EXIT_VEC = $fff8

PRINT = $50

reset:
  ; print the waiting message
  lda #>message
  sta PRINT+1
  lda #<message
  sta PRINT
  jsr print

  ; wait for a key
wait:
  lda SERIAL
  beq wait

  ; clear the screen
  lda #$11
  sta SERIAL

  ; start the cartridge program
  jsr run_program
  jmp reset

run_program:
  jmp CS1

; write the address of a null-terminated string to PRINT
; modifies: a, y
print:
  ldy #0
_print_loop:
  lda (PRINT),y
  beq _print_done
  sta SERIAL
  iny
  jmp _print_loop
_print_done:
  rts

message:
  .byte $11, "Press any key to start...", 0

  .org EXIT_VEC
  .word reset

; reset vector
  .org  $fffc
  .word reset
