  .org $8003

; memory map:
SERIAL = $8002

; monitor subroutines:
; TODO: include copies of these in this program
get_key  = $c046
hex_byte = $c13b
get_byte = $c14c

; ascii codes:
NEWLINE = $0a

; memory allocation:
opc_buf     = $20    ; 3 bytes 
opc_handler = $23    ; 2 bytes
insert_ptr  = $25    ; 2 bytes

main:
  lda #02
  sta insert_ptr+1
  lda #00
  sta insert_ptr
mainloop:
  lda #NEWLINE
  sta SERIAL
  jsr print_addr
  jsr get_key
  sta opc_buf
  jsr get_key
  sta opc_buf+1
  jsr get_key
  sta opc_buf+2

  ldx #0            ; start checking at the first opcode in the table
dispatch_loop:
  jsr dispatch      ; run the opcode handler if it matches and move on
  cpy #1            ; if a match was not found,
  bne dispatch_loop ; keep going.
  cpx #249          ; if the table is exhausted,
  bcs _dispatch_loop_fail   ; the opcode is unknown. 
  jmp mainloop      ; otherwise, read the next opcode
_dispatch_loop_fail:
  jmp bad_handler

; increment the insertion pointer
inc_insert:
  inc insert_ptr
  bne _inc_insert_done
  inc insert_ptr+1
_inc_insert_done:
  rts

; insert the a register and move on
insert_a:
  ldy #0
  sta (insert_ptr),y
  jsr inc_insert
  rts

; insert the x and a registers and move on
insert_ax:
  ldy #0
  pha
  txa
  sta (insert_ptr),y
  jsr inc_insert
  pla
  sta (insert_ptr),y
  jsr inc_insert
  rts

; get a value in hex, and return it in A (TODO: support binary (%) and decimal)
get_val:
  jsr get_key
  cmp #"$"
  bne _get_val_not_hex
  jsr get_byte
  rts
_get_val_not_hex:

  cmp #$22 ; double quote
  bne _get_val_not_char
  jsr get_key
  pha
  jsr get_key
  pla
  rts

_get_val_not_char:
  jmp bad_handler

; get a word in hex and return it in a and x
get_word:
  jsr get_key
  cmp #"$"
  bne _get_word_fail
  jsr get_byte
  pha
  jsr get_byte
  tax
  pla
  rts
_get_word_fail:
  jmp bad_handler

; print the insertion pointer
print_addr:
  lda insert_ptr+1
  jsr hex_byte
  stx SERIAL
  sty SERIAL
  lda insert_ptr
  jsr hex_byte
  stx SERIAL
  sty SERIAL
  lda #":"
  sta SERIAL
  lda #" "
  sta SERIAL
  rts

; 1. match the xth element in the opcode table with the input buffer
; 2. if it matches, call the opcode handler
; 3. increment x by 5
; 4. return in y 1 if the opcode matched, otherwise 0
dispatch:
  lda opcode_table,x
  cmp opc_buf
  bne _dispatch_miss_1
  inx
  lda opcode_table,x
  cmp opc_buf+1
  bne _dispatch_miss_2
  inx
  lda opcode_table,x
  cmp opc_buf+2
  bne _dispatch_miss_3
  inx

  lda opcode_table,x
  sta opc_handler
  lda opcode_table+1,x
  sta opc_handler+1

  ; there is no indirect jsr, so we do this
  jsr _dispatch_run
  ldy #1
  rts
_dispatch_run:
  jmp (opc_handler)

_dispatch_miss_3:
  dex
_dispatch_miss_2:
  dex
_dispatch_miss_1:
  inx
  inx
  inx
  inx
  inx
  ldy #0
  rts

; opcode handlers:
lda_handler:
  jsr get_key
  cmp #"#"
  bne bad_handler ; TODO: add support for other addressing modes
  lda #$a9        ; insert the opcode
  jsr insert_a
  jsr get_val     ; insert the immediate value
  jsr insert_a
  rts
sta_handler:
  lda #$8d
  jsr insert_a
  jsr get_word
  jsr insert_ax
  rts

rts_handler:
  lda #$60
  jsr insert_a
  rts

; not a subroutine like the others, you can jump here if you
; encounter an error in parsing
bad_handler:
  brk
  lda #":"
  sta SERIAL
  lda #"("
  sta SERIAL
  jmp mainloop

; note to self: make sure to order these roughly by usage, so that
; dispatching is faster
opcode_table:
  .byte "lda"
  .word lda_handler
  .byte "sta"
  .word sta_handler
  .byte "rts"
  .word rts_handler
