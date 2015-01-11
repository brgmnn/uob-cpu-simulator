# 'br' test case code
# modifying this code with cause tests to fail!

	br r0,$1
	mov r1,#1	
	br r1,$end
1:
	mov r0,#2
end:
	halt
