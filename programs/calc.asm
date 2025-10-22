  .org $c003

SERIAL = $8002
CLEAR =    $11
NEWLINE =  $a

; memory allocation:
PRINT = $50        ; 2 bytes

A = 5
B = 2

reset:
    ; A
    lda #"0" + A
    sta SERIAL
    
    ; +
    lda #add
    sta PRINT
    lda #>add
    sta PRINT+1
    jsr print
    
    ; B
    lda #"0" + B
    sta SERIAL
    
    ; =
    lda #equals
    sta PRINT
    lda #>equals
    sta PRINT+1
    jsr print

    ; A + B
    lda #"0" + A
    adc #B
    sta SERIAL

    ; \n
    lda #NEWLINE
    sta SERIAL

    ; A
    lda #"0" + A
    sta SERIAL
    
    ; -
    lda #minus
    sta PRINT
    lda #>minus
    sta PRINT+1
    jsr print
    
    ; B
    lda #"0" + B
    sta SERIAL
    
    ; =
    lda #equals
    sta PRINT
    lda #>equals
    sta PRINT+1
    jsr print

    ; A - B
    lda #"0" + A
    sbc #B
    sta SERIAL

done:
  jmp done

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

add:
    .byte " + ", 0
minus:
    .byte " - ", 0
equals:
    .byte " = ", 0

; reset vector
  .org  $fffc
  .word reset