# 'load' test case code
# modifying this code with cause tests to fail!

	mov  r0,$data
	load r1,r0
	add  r0,r0,#4
	load r2,r0
	add  r0,r0,#4
	load r3,r0
	add  r0,r0,#4
	load r4,r0
	halt

data:
	d.int 40
	d.int 30
	d.int 20
	d.int 10

	d.byte 4
	d.byte 9