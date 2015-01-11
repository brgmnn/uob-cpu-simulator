# 'mov' test case code
# modifying this code with cause tests to fail!

	mov r0, #1
	mov r1, r0
addr8:
	mov r2, r1
	mov r3, $addr8

	mov q0,#100.0
	mov q1,q0
	mov q2,q1