# 'div' test case code
# modifying this code with cause tests to fail!

	mov r0, #12
	mov r1, #4
	div r2, r0, r1
	mov r0, #56
	mov r1, #8
	div r3, r0, r1

	mov q0, #12.0
	mov q1, #4.0
	div q2, q0, q1
	mov q0, #56.0
	mov q1, #8.0
	div q3, q0, q1