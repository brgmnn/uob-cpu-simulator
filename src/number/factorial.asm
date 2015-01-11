# recursive factorial program

	spr $stack
	mov r1,#10

	call $factorial
	halt

# calculates the factorial of a number
# r0 = fact(r1)
factorial:
	br r1,$factr
	mov r0,#1
	return
factr:
	push r1
	sub r1,r1,#1
	call $factorial
	pop r3
	mul r0,r0,r3
	return

stack: