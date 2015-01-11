# 'nbr' test case code
# modifying this code with cause tests to fail!

	nbr r0,$1
	mov r1,#1	
	nbr r1,$end
1:
	mov r0,#2
end:
	halt
