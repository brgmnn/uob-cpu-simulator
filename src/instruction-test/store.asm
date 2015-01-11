# 'store' test case code
# modifying this code with cause tests to fail!

	mov   r1,#1234
	mov   r2,#4321
	mov   r3,#9999
	mov   r4,#1111
	mov   r0,$data
	store r1,r0
	add   r0,r0,#4
	store r2,r0
	add   r0,r0,#4
	store r3,r0
	add   r0,r0,#4
	store r4,r0
	halt

data:
	d.int 40
	d.int 30
	d.int 20
	d.int 10