  .org $8003

SERIAL = $8002

; memory allocation:
PRINT = $50           ; 2 bytes

BACKSPACE = $08
DELETE =    $7f
NEWLINE =   $0a
ESCAPE =    $1b

reset:
  ; wait in a loop for a key to be pressed and put it in a
  lda SERIAL
  beq reset

  ; escape has to be handled separately so that we can rts from the program
  ; itself
  cmp #ESCAPE
  beq done

  ; handle the keypress
  jsr character

  ; go back and wait for the next key
  jmp reset

done:
  lda #NEWLINE
  sta SERIAL
  rts

; handle a single keypress (from the a register)
; modifies: x, y
character:
  cmp #DELETE
  beq _character_backspace

  ; just output or keys directly
  sta SERIAL

  rts

_character_backspace:
  ldx #BACKSPACE
  stx SERIAL
  ldy #" "
  sty SERIAL
  stx SERIAL
  rts

; print a null-terminated string pointed to by PRINT
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