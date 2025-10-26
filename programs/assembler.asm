  .org $8003

; memory map:
SERIAL   = $8002
EXIT_VEC = $fff8

; ascii codes:
ESCAPE    = $1b
CLEAR     = $11
NEWLINE   = $0a
DELETE    = $7f
BACKSPACE = $08

; memory allocation:
PRINT        = $50      ; 2 bytes
BYTE_BUILD   = $40      ; 1 byte
CURRENT_ADDR = $30      ; 2 bytes

main:
  ; start writing to $0200 (after the zero page and stack)
  lda #00
  sta CURRENT_ADDR
  lda #02
  sta CURRENT_ADDR+1

  lda #welcome_message
  sta PRINT
  lda #>welcome_message
  sta PRINT+1
  jsr print

  jsr print_addr

loop:
  ; get a byte
  jsr get_byte

  ; write it to the address
  ldy #0
  sta (CURRENT_ADDR),y

  ; increment the memory address
  inc CURRENT_ADDR    ; increment low byte
  bne inc_didnt_carry ; if it didn’t overflow, we’re done
  inc CURRENT_ADDR+1  ; else, increment high byte
inc_didnt_carry:

  jmp loop

; print the current memory address
; modifies: a, x, y
print_addr:
  ; print the address
  lda CURRENT_ADDR+1
  jsr hex_byte
  stx SERIAL
  sty SERIAL
  lda CURRENT_ADDR
  jsr hex_byte
  stx SERIAL
  sty SERIAL

  ; print ': #
  lda #":"
  sta SERIAL
  lda #" "
  sta SERIAL

  rts

; return (in a) a single key, ignoring spaces
; modifies: a (duh)
get_key:
  lda SERIAL
  beq get_key           ; if no char was typed, check again.

  cmp #ESCAPE           ; if escape was pressed,
  beq _get_key_exit     ; return to the system monitor
  cmp #"@"              ; if "@" was pressed,
  beq _get_key_new_addr ; change address

  sta SERIAL             ; echo back the char.

  cmp #" "               ; if space was pressed,
  beq get_key            ; wait for the next key.
  cmp #NEWLINE           ; if newline was pressed,
  beq _get_key_newline   ; handle it.
  cmp #";"               ; if space was pressed,
  beq _get_key_comment   ; start a comment.

  rts
_get_key_exit:
  lda #NEWLINE
  sta SERIAL
  sta SERIAL
  jmp EXIT_VEC
_get_key_newline:
  ; show the latest memory address
  jsr print_addr
  ; exit
  jmp get_key
_get_key_new_addr:
  lda #NEWLINE
  sta SERIAL
  sta SERIAL

  jsr get_byte
  sta CURRENT_ADDR+1
  jsr get_byte
  sta CURRENT_ADDR

  lda #":"
  sta SERIAL
  lda #" "
  sta SERIAL

  jmp get_key
_get_key_comment:
  lda SERIAL                ; read a key.
  sta SERIAL
  cmp #NEWLINE              ; only if it's a newline,
  beq _get_key_newline      ; exit the comment

  cmp #DELETE               ; if they pressed backspace,
  bne _get_key_comment
  lda #BACKSPACE            ; move cursor back
  sta SERIAL
  lda #" "                  ; clear character
  sta SERIAL     
  lda #BACKSPACE            ; move cursor back twice
  sta SERIAL
  jmp _get_key_comment

; wait for a key and return (in a) the value of a single hex char
; modifies: a (duh)
get_nibble:
  jsr get_key
  cmp #$3a
  bcc _get_nibble_digit
  sec
  sbc #"a" - 10
  rts
_get_nibble_digit:
  sbc #"0" - 1
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

; wait for a key and return (in a) the value of a byte (2 hex chars)
; modifies: a (duh)
get_byte:
  ; get the MS nibble and move it to the MS area of the a reg
  jsr get_nibble
  asl
  asl
  asl
  asl
  ; move the MSN to memory
  sta BYTE_BUILD

  ; get the LSN and combine it with the MSN
  jsr get_nibble
  ora BYTE_BUILD
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

welcome_message:
  .byte CLEAR, ESCAPE, "[7m"
  .byte " O64 Assembler v1.0.1 "
  .byte ESCAPE, "[0m", NEWLINE

  .byte "TIP: Use '@' to move to a different address", NEWLINE

  .byte NEWLINE, 0

equals:
  .byte " = ", 0