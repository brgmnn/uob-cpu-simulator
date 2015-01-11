# livermore loop --- inner product
# 
# follows this algorithm:
# for (l=1; l<=loop; l++) {
#     q = 0;
#     for ( k=0 ; k<n ; k++ ) {
#         q += z[k]*x[k];
#     }
#     print q
# }

	mov r0,#10

outerloop:
	sub r0,r0,#1
	mov r1,#50
	mov r2,#0
	mov r5,$z
	mov r6,$x
innerloop:
	load r3,r5
	load r4,r6
	sub r1,r1,#1
	add r5,r5,#4
	add r6,r6,#4
	mul r7,r3,r4
	add r2,r2,r7
	br r1,$innerloop

	print r0
	br r0,$outerloop

z:
	d.int 17
	d.int 55
	d.int 0
	d.int 56
	d.int 97
	d.int 56
	d.int 87
	d.int 29
	d.int 57
	d.int 22
	d.int 57
	d.int 25
	d.int 70
	d.int 72
	d.int 14
	d.int 8
	d.int 41
	d.int 12
	d.int 67
	d.int 26
	d.int 39
	d.int 33
	d.int 40
	d.int 48
	d.int 33
	d.int 1
	d.int 31
	d.int 45
	d.int 60
	d.int 81
	d.int 82
	d.int 9
	d.int 35
	d.int 25
	d.int 82
	d.int 32
	d.int 55
	d.int 95
	d.int 10
	d.int 0
	d.int 74
	d.int 29
	d.int 10
	d.int 24
	d.int 58
	d.int 82
	d.int 99
	d.int 37
	d.int 37
	d.int 73

x:
	d.int 37
	d.int 52
	d.int 80
	d.int 93
	d.int 75
	d.int 82
	d.int 13
	d.int 16
	d.int 40
	d.int 73
	d.int 38
	d.int 11
	d.int 4
	d.int 50
	d.int 37
	d.int 80
	d.int 90
	d.int 0
	d.int 20
	d.int 9
	d.int 98
	d.int 50
	d.int 90
	d.int 5
	d.int 14
	d.int 42
	d.int 39
	d.int 27
	d.int 37
	d.int 74
	d.int 15
	d.int 70
	d.int 71
	d.int 14
	d.int 80
	d.int 7
	d.int 72
	d.int 15
	d.int 85
	d.int 46
	d.int 4
	d.int 5
	d.int 22
	d.int 79
	d.int 93
	d.int 23
	d.int 43
	d.int 49
	d.int 84
	d.int 68
