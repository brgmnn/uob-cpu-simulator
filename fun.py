#!/usr/bin/env python
import random

# for i in range(50):
# 	# print random.randint(0,2147483647) # 0 <= x <= 2^31 -1
# 	print "\td.int",random.randint(0,99)

img = [
	1, 1, 1, 1, 1,
	1, 1, 81, 1, 1,
	1, 1, 1, 1, 1,
	1, 1, 1, 1, 1,
	1, 1, 1, 1, 1
]

imgblurred = [0 for i in range(25)]

def pixel(x,y):
	x, y = x-1, y-1
	x1 = x
	val = 0

	for j in range(3):
		x = x1 % 5
		for i in range(3):
			pos = ((5*y)+x) % 25
			val += img[pos]
			# print pos
			# print img[pos]
			x = (x+1) % 5
		y = (y+1) % 5

	return val/9

for y in range(5):
	for x in range(5):
		pos = ((5*y)+x)%25
		imgblurred[pos] = pixel(x,y)
		print imgblurred[pos]

