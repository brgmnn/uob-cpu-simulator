# tests the stack

	spr $stack

	mov r0,#10
	push r0
	mov r0,#20
	push r0
	mov r0,#5
	print r0
	pop r0
	print r0
	pop r0
	print r0


	mov r1,#7
	mov r2,#13
	push r1
	push r2
	call $func1
	pop r0
	print r0

	halt

func1:
	pop r30
	pop r2
	pop r1
	
	add r0,r1,r2
	push r0
	push r30
	return

stack: