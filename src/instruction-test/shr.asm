# left shift instruction
# equivalent to a = b << c
# for shl ra,rb,rc

	mov r2,#32
	mov r3,#3
	shr r0,r2,#2
	shr r1,r2,r3
	shr r4,r2,#5
	shr r5,r2,#7
	halt