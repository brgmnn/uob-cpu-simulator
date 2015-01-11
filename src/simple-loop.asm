# this is a comment

	mov r0,#10
	mov r1,#1

loop1:
	sub r0,r0,#1
	add r2,r2,r1
	br r0,$loop1
	halt
