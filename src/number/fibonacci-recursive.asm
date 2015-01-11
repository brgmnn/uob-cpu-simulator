# Fibonacci number sequence generator.
# Generates up to the n+2 th number in the fibonacci series.
# Stores the series in memory starting from $values
# r0 = stack pointer

	spr #4000

	mov r1,#3
	push r1
	call $fibonacci
	pop r0
	halt


# gets the nth fibonacci number. using recursive calls.
# r0 = getfib(r1) where r1 = iths fib number, r2 is where the result is stored.
fibonacci:
	# note we must first pop the link register
	pop r30
	pop r1
	push r30
	sub r2,r1,#1
	nbr r2,$one
	nbr r1,$zero
	
	sub r1,r1,#1

	push r1
	call $fibonacci
	pop r3
	nbr r1,$skip1

	sub r1,r1,#1
	push r1
	call $fibonacci
	pop r4
	jmp $skip2

skip1:
	mov r4,#0
skip2:
	add r0,r3,r4
	pop r30
	push r0
	push r30
	return

one:
	# base case for i=1
	mov r0,#1
	pop r30
	push r0
	push r30
	return
zero:
	# base case for i=0
	mov r0,#0
	# push our return argument on the stack
	pop r30
	push r0
	push r30
	return

values:
	d.int 0
	d.int 0
	d.int 0
	d.int 0
	d.int 0
	d.int 0
	d.int 0
	d.int 0
	d.int 0
	d.int 0
