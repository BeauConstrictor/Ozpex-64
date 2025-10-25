  .org $8003

SERIAL   = $8002
CLEAR    =   $11
DELETE   =   $7f
NEWLINE  =   $0a
ESCAPE   =   $1b

SLOT2    = $a003
SLOT2END = $c002

; memory allocation:
BUFPTR =   $20        ; 1 byte
BUFFER = $0201        ; 256 bytes

  jsr init
  jsr load_buffer
  jsr redraw
main:
  lda SERIAL
  beq main

  cmp #ESCAPE
  beq escape

  jsr write_char
  jsr redraw

  jmp main

escape:
  jsr save_buffer

  lda #NEWLINE
  sta SERIAL

  rts

; clear & draw the screen contents
; modifies: a, x
redraw:
  lda #CLEAR
  sta SERIAL
  jsr print_message
  jsr print_buffer
  rts

; initialise memory
init:
  lda #0
  sta BUFPTR
  rts

; append the character in the a register to the text buffer
; modifies: x
write_char;
  cmp #DELETE
  beq _write_char_delete

  ldx BUFPTR
  inx
  sta BUFFER,x
  inc BUFPTR
  rts
_write_char_delete:
  dec BUFPTR
  rts

; display the contents of the text buffer
; modifies: a, x
print_buffer:
  ; will immediately wrap because of the increment
  ldx #$ff
_print_buffer_loop:
  inx
  lda BUFFER,x
  sta SERIAL

  ; print up to the end of the buffer
  cpx BUFPTR
  bne _print_buffer_loop
  rts

; write the contents of slot to to the text buffer
; modifies: a, x
save_buffer:
  ; will immediately wrap because of the increment
  ldx #$ff
_save_buffer_loop:
  inx

  lda BUFFER,x
  sta SLOT2,x

  lda BUFPTR
  sta SLOT2END

  cpx BUFPTR
  bne _save_buffer_loop
  rts

; write the contents of the text buffer to slot 2
; modifies: a, x
load_buffer:
  lda SLOT2END
  sta BUFPTR

  ; will immediately wrap because of the increment
  ldx #$ff
_load_buffer_loop:
  inx

  lda SLOT2,x
  sta BUFFER,x

  lda BUFPTR
  sta SLOT2END

  cpx BUFPTR
  bne _load_buffer_loop
  rts

; print the title message
; modifies: a, x
print_message:
  ldx #0
_print_loop:
  lda message,x
  beq _print_done
  sta SERIAL
  inx
  jmp _print_loop
_print_done:
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

message:
  .byte "Ozpex 64 Text Editor", NEWLINE
  .byte "Press ESC to save to Slot 2 and exit.", NEWLINE, NEWLINE, 0