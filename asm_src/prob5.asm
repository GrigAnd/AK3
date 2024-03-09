        SECTION .data
div:    db 10
step:   db 2520
x:      db 2520
tmp:    db 2520
c21:    db 21

        SECTION .text
_loop20:
        LD  x
        ST  tmp
        ST  step
        LD div ; div++
        INC
        ST div

        SUB c21 ; if div=21 goto _end
        JZ _end

_inc:
        LD  x   ; x++
        ADD step
        ST  x
        ST  tmp

_sub:
        LD tmp   ; x=x//div
        DIVR div
        ST tmp
        JZ  _loop20 ; if x=0 goto _loop20
        JMP _inc ; else goto _inc

_end:
        LD x
        ST 4242