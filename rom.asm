  .org $d000

reset:
  lda $c000
  lda $c001
  lda $c002
  lda $c003
  lda $c004
  lda $c005
  lda $c006
  lda $c007
  lda $c008
  lda $c009
  lda $c00a
  lda $c00b
  lda $c00c

  .org  $fffc
  .word reset