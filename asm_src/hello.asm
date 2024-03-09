        SECTION .data
hello:  db "hello world"
&hello: db hello
ptr:    db 0
len:    db 0

        SECTION .text
_start:
        LD [&hello]     ; hello[0]
        ST len
        LD &hello       ; ptr = &hello
        ST ptr          ; ptr = &hello
_loop:
        LD  ptr
        INC
        ST  ptr         ; ptr++
        LD  [ptr]       ; buf = *ptr
        ST  4242        ; output buffer
        LD  len
        DEC
        ST  len         ; len--
        JNZ _loop       ; if len != 0, goto _loop_prompt