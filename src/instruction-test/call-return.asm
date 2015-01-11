# 'call'/'return' test case code
# modifying this code with cause tests to fail!

	mov r1,#10

loop1:
	call $func1
	sub r1,r1,#1
	br r1,$loop1

	mov r1,#15
loop2:
	call $func1
	sub r1,r1,#1
	br r1,$loop2	
	halt


func1:
	add r0,r0,#1
	return
