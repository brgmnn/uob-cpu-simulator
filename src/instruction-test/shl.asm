# left shift instruction
# equivalent to a = b << c
# for shl ra,rb,rc

	mov r2,#4
	mov r3,#3
	shl r0,r2,#2
	shl r1,r2,r3
	mov r5,#1
	shl r6,r5,#35
	halt