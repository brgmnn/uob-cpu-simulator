# /*
#      *******************************************************************
#      *   Kernel 1 -- hydro fragment
#      *******************************************************************
#      *       DO 1 L = 1,Loop
#      *       DO 1 k = 1,n
#      *  1       X(k)= Q + Y(k)*(R*ZX(k+10) + T*ZX(k+11))
#      */

#     for ( l=1 ; l<=loop ; l++ ) {
#         for ( k=0 ; k<n ; k++ ) {
#             x[k] = q + y[k]*( r*z[k+10] + t*z[k+11] );
#         }
#     }
#     argument = 1;
#     TEST( &argument );




	mov r0,#10
loop1:
	sub r0,r0,#1

	mov r1,#10
	mov r5,#0
loop2:
	sub r1,r1,#1

	mov r9,$z
	mul r8,r5,#4
	add r9,r9,#40
	add r8,r8,r9

	# r*z[k+10]
	load r4,r8
	mul r3,r4,#3

	# t*z[k+11]
	add r10,r8,#4
	sub r8,r8,#44
    load r7,r10
	sub r8,r8,$z
    mul r6,r7,#4

	add r8,r8,$y

	
	# y[k]*(...)
	load r4,r8
	sub r8,r8,$y
    add r3,r3,r6

	add r8,r8,$x
    add r2,r3,#10

	store r2,r8

	add r5,r5,#1
	br r1,$loop2

	br r0,$loop1



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

y:
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

x: