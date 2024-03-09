        SECTION .data
prompt:     db "What is your name?"
prompt_ptr: db prompt           ; prompt_ptr = &prompt
greet:      db "Hello, "
greet_ptr:  db greet            ; greet_ptr = &greet
n_char:     db 10               ; \n
after:      db 33               ; "!"
ptr:        db 0
len:        db 0
buf:        db 0                ; input buffer
name:       db 20       dup     ; name
name_ptr:   db name             ; name_ptr = &name


        SECTION .text
_start:
        LD  [prompt_ptr]        ; *prompt_ptr = prompt[0]
        ST  len
        LD  prompt_ptr          ; ptr = prompt_ptr
        ST  ptr                 ; ptr = prompt_ptr
_loop_prompt:
        LD  ptr
        INC
        ST  ptr                 ; ptr++
        LD  [ptr]               ; buf = *ptr
        ST  4242                ; output buffer
        LD  len
        DEC
        ST  len                 ; len--
        JNZ _loop_prompt        ; if len != 0, goto _loop_prompt

        LD  n_char              ; \n
        ST  4242                ; output buffer

        CLR
        ST len                  ; len = 0
        LD name_ptr
        INC
        ST ptr                  ; ptr = &name[1]

_loop_name_in:
        LD  4343                ; input
        ST  buf                 ; buf = input
        SUB n_char              ; buf -= '\n'
        JZ  _store_name_len     ; if buf == '\n', goto _store_name_len
        LD  buf
        ST  [ptr]               ; *ptr = buf
        LD  ptr
        INC
        ST  ptr                 ; ptr++
        LD  len
        INC
        ST  len                 ; len++
        JMP _loop_name_in


_store_name_len:
        LD len
        ST name                 ; name[0] = len


        LD [greet_ptr]          ; *greet_ptr = greet[0]
        ST len 
        LD greet_ptr
        ST ptr                  ; ptr = &greet[0]
_loop_greet:
        LD  ptr
        INC
        ST  ptr                 ; ptr++
        LD  [ptr]               ; buf = *ptr
        ST  4242                ; output
        LD  len
        DEC
        ST  len                 ; len--
        JNZ _loop_greet         ; if len != 0, goto _loop_greet


        LD [name_ptr]           ; *name_ptr = name[0]
        ST len 
        LD name_ptr
        ST ptr                  ; ptr = &name[0]
_loop_name_out:
        LD  ptr
        INC
        ST  ptr                 ; ptr++
        LD  [ptr]               ; buf = *ptr
        ST  4242                ; output
        LD  len
        DEC
        ST  len                 ; len--
        JNZ _loop_name_out      ; if len != 0, goto _loop_greet


_print_after:
        LD after
        ST 4242                 ; output buffer