# bubblesort algorithm

	mov r0,#9
	mov r1,$data

checkall:
	sub r0,r0,#1

	# loads the values in m[r0] and m[r0+1]
	load r10,r1
	add  r1,r1,#4
	load r11,r1

	# compares if m[r0] > m[r0+1] branch to noswap if false
	gt  r12,r10,r11
	nbr r12,$noswap

	# swaps m[r0] with m[r0+1]
	store r10,r1
	sub   r1,r1,#4
	store r11,r1
	add   r1,r1,#4 

	# marks this pass as dirty
	mov r4,#1
noswap:
	br   r0,$checkall
	# halt
	nbr  r4,$finish

	mov r1,$data
	mov r0,#9
	mov r4,#0
	jmp $checkall
finish:
	halt




data:
	d.int 10
	d.int 9
	d.int 8
	d.int 7
	d.int 6
	d.int 5
	d.int 4
	d.int 3
	d.int 2
	d.int 1
	