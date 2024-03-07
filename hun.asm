	SECTION	.data
prompt:	db	"What is your name?"
greet:	db	"Hello, "
after:	db	21 ; !
ptr:	db	0
len:	db	0
stop:	db	10
buf:	db	0
name:	db	20	dup


	SECTION	.text
_start:
	LD 	[prompt]
	ST	len

_loop_prompt:	
	LD	prompt
	INC
	ST	ptr
	LD	[ptr]
	ST 	4242	; output buffer
	LD	[len]
	DEC
	ST	len
	JNZ	_loop_prompt

	CLR
	ST 	len
	LD	name
	INC
	ST	ptr

_loop_name_in:
	LD	4343	; input buffer
	ST	buf
	SUB	stop
	JZ	_store_name_len
	LD	buf
	ST	[ptr]
	LD	[ptr]
	INC
	ST	ptr
	LD	[len]
	INC
	ST	len
	JMP	_loop_name_in

_store_name_len:
	LD	[len]
	ST	name

_loop_greet:
	LD	greet
	INC
	ST	ptr
	LD	[ptr]
	ST 	4242	; output buffer
	LD	[len]
	DEC
	ST	len
	JNZ	_loop_greet

_loop_name_out:
	LD	greet
	INC
	ST	ptr
	LD	[ptr]
	ST 	4242	; output buffer
	LD	[len]
	DEC
	ST	len
	JNZ	_loop_name_out

_print_after:
	LD	[after]
	ST	4242	; output buffer