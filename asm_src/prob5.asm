        SECTION .data
div:    db 0
step:   db 2520
x:      db 2520
max:    db 21

        SECTION .text

_inc_div:
        LD div
        INC
        ST div
        SUB max
        JZ _end

_loop:
        LD x
        DIVR div
        JZ _inc_div
        LD x
        ADD step
        ST x
        CLR
        INC
        ST div
        JMP _loop

_end:
        LD x
        HLT