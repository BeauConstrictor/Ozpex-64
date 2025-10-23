  .org $c003

SERIAL = $8002
CLEAR =    $11
NEWLINE =  $a

ROM = $c003
SLOT1 = $8003
SLOT2 = $a003

; memory allocation:
PRINT = $50        ; 2 bytes
BYTE_BUILD = $60   ; 1 byte
WORD_LOCATION = $70         ; 2 bytes

reset:
  lda #boot_msg
  sta PRINT
  lda #>boot_msg
  sta PRINT+1
  jsr print

command_loop:
  jsr command
  jmp command_loop

; show the prompt, run a full command and return
; modifies: a, y
command:
  lda #prompt
  sta PRINT
  lda #>prompt
  sta PRINT+1
  jsr print
_command_wait_for_key:
  jsr get_key

  cmp #"c"
  beq _command_clear
  cmp #"r"
  beq _command_read
  cmp #"w"
  beq _command_write
  cmp #"j"
  beq _command_jump
  cmp #"x"
  beq _command_execute
  cmp #NEWLINE
  beq _command_skip

  ; unknown command type, print error message
  lda #unknown_command_mode_msg
  sta PRINT
  lda #>unknown_command_mode_msg
  sta PRINT+1
  jsr print
  rts

_command_skip:
  rts
_command_clear:
  lda #$11 ; device control 1 (clear)
  sta SERIAL
  rts
_command_read:
  jsr get_byte
  sta WORD_LOCATION+1
  jsr get_byte
  sta WORD_LOCATION
  ldy #0
  lda (WORD_LOCATION),y

  ; print the ascii char for the value
  ldx #NEWLINE
  stx SERIAL
  ldx #"'"
  stx SERIAL

  sta SERIAL

  ldx #"'"
  stx SERIAL
  ldx #NEWLINE
  stx SERIAL

  ; print the hex representation of the value
  ldx #"$"
  stx SERIAL

  jsr hex_byte
  stx SERIAL
  sty SERIAL

  ldx #NEWLINE
  stx SERIAL

  rts
_command_write:
  jsr get_byte
  sta WORD_LOCATION+1
  jsr get_byte
  sta WORD_LOCATION

  jsr get_byte

  ldy #0
  sta (WORD_LOCATION),y
  
  sty SERIAL
  stx SERIAL

  rts
_command_jump:
  jsr get_byte
  sta WORD_LOCATION+1
  jsr get_byte
  sta WORD_LOCATION

  jmp (WORD_LOCATION)

  rts
_command_execute:
  jsr get_key

  cmp #"1"
  beq _command_execute_slot1
  cmp #"2"
  beq _command_execute_slot2
  cmp #"3"
  beq _command_execute_rom
   ; unknown location
   lda #unknown_exec_location_msg
  sta PRINT
  lda #>unknown_exec_location_msg
  sta PRINT+1
  jsr print
  rts
_command_execute_slot1:
  jmp SLOT1
_command_execute_slot2:
  jmp SLOT2
_command_execute_rom:
  jmp ROM

; return (in a) a single key, ignoring spacea
; modifies: a (duh)
get_key:
  lda SERIAL
  beq get_key ; if no char was typed, check again.
  sta SERIAL  ; echo back the char.
  cmp #" "    ; if space was pressed,
  beq get_key ; wait for the next key.
  rts

; wait for a key and return (in a) the value of a single hex char
; modifies: a (duh)
get_nibble:
  jsr get_key
  cmp #$3a
  bcc _get_nibble_digit
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

boot_msg:
  .byte CLEAR
  .byte "Welcome to Ozpex 64 (2025)", NEWLINE
  .byte "Monitor: READY", NEWLINE
  .byte 0

unknown_command_mode_msg:
  .byte " - unknown command!", NEWLINE
  .byte 0

unknown_exec_location_msg:
  .byte " - unknown location!", NEWLINE
  .byte 0

prompt:
  .byte NEWLINE
  .byte "? "
  .byte 0

; reset vector
  .org  $fffc
  .word reset