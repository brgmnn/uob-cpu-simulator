# does a gaussian blur on a .pgm image

	spr #700000

	# reads in the width (x) and height (y)
	io.read r20
	io.read r21
	mul r22,r20,r21

	# write out the image header for our image
	io.putc #80
	io.putc #50
	io.putc #10
	io.putc #35
	io.putc #10
	io.write r20
	io.putc #32
	io.write r21
	io.putc #10
	io.read r19
	io.write r19

	mov r19,r22
	mov r18,$image
copyimg:
	sub r19,r19,#1
	io.read r17
	store r17,r18
	add r18,r18,#4
	# print r19
	br r19,$copyimg
	# iterations of blur
	mov r23,#1
	# halt



iterations:
	sub r23,r23,#1

	# ypos
	mov r1,r21
	mov r3,#0
loopy:
	sub r1,r1,#1
	io.putc #10	
	
	# xpos
	mov r0,r20
	mov r2,#0
loopx:
	sub r0,r0,#1

	# call the gaussian blur function
	push r2
	push r3
	call $pixel
	pop r10

	# write that pixels data
	io.write r10
	io.putc #32

	# branch on x
	add r2,r2,#1
	br r0,$loopx

	print r1

	# branch on y
	add r3,r3,#1
	br r1,$loopy


	br r23,$iterations
	halt


# calculates the value of a pixel and returns it. takes parameters x (r41), y (r42) in the image.
# call as:
# push x
# push y
# call $pixel
# pop val
# workspace from >r40
pixel:
	# pop the arguments from the stack
	pop r63
	pop r42
	pop r41
	push r63

	# start with the upper left hand corner of the image. (take 1 extra to count for index 0)
	v.sub r41,r41,#1
	# sub r41,r41,#1
	# sub r42,r42,#1
	mov r43,r41

	mov r60,#0

	mov r40,#0
	mov r51,#3
kernely:
	mov r50,#3
	mov r41,r43
	mod r42,r42,r21
kernelx:
	mod r41,r41,r20

	# calculate the array index
	mul r45,r42,r21
	add r45,r45,r41
	mod r45,r45,r22
	mul r45,r45,#4
	add r45,r45,$image

	# loads that pixel and adds it to the running total.
	load r46,r45
	add r40,r40,r46
	add r60,r60,#1

	# increment the x position, decrement the xkernel loop counter and branch
	add r41,r41,#1
	sub r50,r50,#1
	br r50,$kernelx

	# increment the y position, decrement the ykernel loop counter and branch
	add r42,r42,#1
	sub r51,r51,#1
	br r51,$kernely

	# divide the output value by 9 because it was averaged with 9 cells.
	div r40,r40,#9

	# push the return value on the stack
	pop r63
	push r40
	push r63
	return

	halt
image:

