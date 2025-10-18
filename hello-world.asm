; the classic "Hello, world!" program. This one outputs to a serial device at
; $ffff. This device functions by relaying what ASCII chars are written to it
; directly over an RS-232 serial connection (if it was real - this one is just
; simulated, so the data gets sent to stdout).

  lda #$11                  ; clear the screen
  sta $ffff

  ldx #0                    ; initalise the loop index
loop:
  lda message,X             ; load byte from message
  beq done                  ; stop at zero terminator
  sta $ffff
  inx
  jmp loop

done:
  jmp done

; data ;

message:
  .BYTE "Hello, world!", 0  ; null-terminated