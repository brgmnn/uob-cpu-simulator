# Fibonacci number sequence generator.
# Generates up to the n+2 th number in the fibonacci series.
# Stores the series in memory starting from $values

# iterations
	mov r10,#45

	mov r11,$values
	add r11,r11,#8
	mov r1,#1
	mov r2,#0

# main loop
loop:
	add r0,r1,r2
	mov r2,r1
	mov r1,r0
	store r0,r11

	add r11,r11,#4
	sub r10,r10,#1
	br r10,$loop
	halt

values:
	d.int 0
	d.int 1