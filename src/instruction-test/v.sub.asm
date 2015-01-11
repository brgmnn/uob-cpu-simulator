# tests vector subtraction

	mov r0,#4
	mov r1,#5
	mov r2,#6
	mov r3,#7
	v.mov r4,#3
	v.sub r8,r0,r4
	v.sub r12,r8,r4

	mov q0,#4.0
	mov q1,#5.0
	mov q2,#6.0
	mov q3,#7.0
	v.mov q4,#3.0
	v.sub q8,q0,q4
	v.sub q12,q8,q4
	halt