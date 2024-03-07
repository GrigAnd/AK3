	SECTION	.data
prompt:	db	"What is your name?"
greet:	db	"Hello, "
after:	db	"!"
ptr:	db	0
lgth:	db	0
stop:	db	10
buffer:	db	5	dup


	SECTION	.text
	LD 	prompt
	ST	lgth
_lp1:	
	LD	(prompt_addr)
	ST	4
	ST	42; output buffer
	DEC
	ST	prompt_addr
	LD	lgth
	DEC
	ST	lgth
	JNZ	_lp1

	LD	43; input buffer
	ST	buffer
	SUB	stop
	JZ	_end
	LD	buffer




	LD lgth
	INC



_end:
	LD	greet
	





	JNZ	lpin

	HLT
