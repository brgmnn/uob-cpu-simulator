# 'mul' test case code
# modifying this code with cause tests to fail!

	mov r1, #6
	mov r2, #8
	mul r0, r1, r2
	mov r4, #0
	mov r5, #10
	mul r3, r4, r5

	mov q1, #6.0
	mov q2, #8.0
	mul q0, q1, q2
	mov q4, #0.0
	mov q5, #10.0
	mul q3, q4, q5