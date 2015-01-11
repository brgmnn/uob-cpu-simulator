# Fibonacci number sequence generator.
# Generates up to the n+2 th number in the fibonacci series.
# No memory so fast.

# iterations
	mov r10,#300
	mov r1,#1
	mov r2,#0

# main loop
loop:
	sub r10,r10,#1
	add r0,r1,r2
	mov r2,r1
	mov r1,r0
	br r10,$loop
	halt
