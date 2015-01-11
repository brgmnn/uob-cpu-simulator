# tests the vector add instruction

	mov r0,#1
	mov r1,#2
	mov r2,#3
	mov r3,#4

	v.add r0,r0,#10
	v.add r4,r4,r2

	mov q0,#1.0
	mov q1,#2.0
	mov q2,#3.0
	mov q3,#4.0

	v.add q0,q0,#10.0
	v.add q4,q4,q2
	halt
