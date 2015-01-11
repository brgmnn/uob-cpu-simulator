# 'jmp' test case code
# modifying this code with cause tests to fail!

	jmp $1
	mov r0,#1	
2:
	mov r0,#2
	jmp $end
1:
	jmp $2
end:
	halt
