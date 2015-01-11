# calculates the hamming weight of an array of integers
# final result is in r0 and should be: 545

# always take
# IPC: 0.640124681213 ins/cycle (4518 instructions total; 7058 cycles total)
# Branch misprediction: 3.6315323295%


# dynamic local
# IPC: 0.619583104772 ins/cycle (4518 instructions total; 7292 cycles total)
# Branch misprediction: 7.08591674048%
# 3.6315323295%

	mov r1,$data
	mov r2,#40

hamloop:
	load r3,r1
	add r1,r1,#4
	sub r2,r2,#1

countbits:
	and r4,r3,#1
	shr r3,r3,#1
	add r0,r0,r4
	br r3,$countbits

	br r2,$hamloop
	halt

data:
	d.int 222262525
	d.int 188126388
	d.int 133089565
	d.int 61957591
	d.int 13845292
	d.int 126900754
	d.int 145022281
	d.int 19034773
	d.int 240144792
	d.int 104980348
	d.int 258128181
	d.int 203220553
	d.int 66773480
	d.int 33526543
	d.int 159591979
	d.int 82889805
	d.int 48248970
	d.int 150421864
	d.int 139466718
	d.int 48988861
	d.int 266359545
	d.int 250378064
	d.int 248044546
	d.int 169026257
	d.int 75258016
	d.int 136767564
	d.int 205085817
	d.int 168595218
	d.int 261068974
	d.int 218718632
	d.int 114736055
	d.int 111258896
	d.int 205877467
	d.int 253036116
	d.int 43964177
	d.int 235850954
	d.int 238220864
	d.int 17058606
	d.int 94643153
	d.int 202076085