#!/usr/bin/env python
import json, sys, struct

length = 64
registers = 128

# fields = {
# 	"opcode": 7,
# 	"register": 7,
# 	"43bit immediate": 43,
# 	"50bit immediate": 50
# }

# form:
#   %i = instruction lexical code (eg. mov, add, mul, shr)
#   %r = integer register (eg. r0, r1, r2...)
#   %n = integer literal (eg. #0, #10, #256)
#   %q = floating point register (eg. q0, q1, q2...)
#   %f = floating point literal (eg. #100.0, #3.1415...)

defaults = {
	"opcode": [],
	"form": ["%i %r %r %r"],
	"writes": [0],
	"group": "arithmetic",
	"cycles": 1,
	"width": 1,
	"blocking": True
}

#*		Instruction Specification
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
ins = {
	# move instructions
	"mov": {
		"form": [
			"%i %r %r",
			"%i %r %n",
			"%i %q %q",
			"%i %q %f"
		],
	},

	# arithmetic instructions
	"add": {
		# adds two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		]
	},
	"sub": {
		# subtracts two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		]
	},
	"mul": {
		# multiplies two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		]
	},
	"div": {
		# divides two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		],
		"cycles": 2
	},
	"mod": {
		# takes the modulus of a number
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		],
		"cycles": 2
	},

	"shl": {
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		] 
	},
	"shr": {
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		] 
	},

	# vector arithmetic instructions
	"v.mov": {
		# moves two vector-vector registers/numbers together
		"form": [
			"%i %r %r",
			"%i %r %n",
			"%i %q %q",
			"%i %q %f"
		],
		"group": "vector-arithmetic",
		"width": 4
	},
	"vs.mov": {
		# moves two vector-scalar registers together
		"form": ["%i %r %r"],
		"group": "vector-arithmetic",
		"width": [4, 1]
	},
	"v.add": {
		# adds two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		],
		"group": "vector-arithmetic",
		"width": 4
	},
	"vs.add": {
		# adds two vector-scalar registers together
		"form": ["%i %r %r %r"],
		"group": "vector-arithmetic",
		"width": [4, 4, 1]
	},
	"v.sub": {
		# subtracts two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		],
		"group": "vector-arithmetic",
		"width": 4
	},
	"vs.sub": {
		# subtracts two vector-scalar registers together
		"form": ["%i %r %r %r"],
		"group": "vector-arithmetic",
		"width": [4, 4, 1]
	},
	"v.mul": {
		# multiplies two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		],
		"group": "vector-arithmetic",
		"width": 4
	},
	"vs.mul": {
		# multiplies two vector-scalar registers together
		"form": ["%i %r %r %r"],
		"group": "vector-arithmetic",
		"width": [4, 4, 1]
	},
	"v.div": {
		# divides two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
			"%i %q %q %q",
			"%i %q %q %f"
		],
		"group": "vector-arithmetic",
		"width": 4,
		"cycles": 2
	},
	"v.mod": {
		# divides two registers/numbers together
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		],
		"group": "vector-arithmetic",
		"width": 4,
		"cycles": 2
	},
	"vs.div": {
		# divides two vector-scalar registers together
		"form": ["%i %r %r %r"],
		"group": "vector-arithmetic",
		"width": [4, 4, 1],
		"cycles": 2
	},

	# comparison
	"gt": {
		"form": ["%i %r %r %r", "%i %q %q %q"]
	},
	"gte": {
		"form": ["%i %r %r %r", "%i %q %q %q"]
	},
	"eq": {
		"form": ["%i %r %r %r", "%i %q %q %q"]
	},

	# load/store
	"load": {
		"form": [
			"%i %r %r",
			"%i %r %n",
			"%i %q %r",
			"%i %q %n"
		],
		"group": "load-store",
		"cycles": 1
	},
	"store": {
		"form": [
			"%i %r %r",
			"%i %r %n",
			"%i %q %r",
			"%i %q %n"
		],
		"writes": [],
		"group": "load-store",
		"cycles": 1
	},
	"push": {
		"form": ["%i %r", "%i %q"],
		"writes": [],
		"group": "load-store",
	},
	"pop": {
		"form": ["%i %r", "%i %q"],
		"writes": [0],
		"group": "load-store",
	},
	"spr": {
		"form": ["%i %r", "%i %n"],
		"writes": [],
		"group": "load-store",
	},

	# IO
	"io.read": {
		"form": ["%i %r", "%i %q"],
		"writes": [0],
		"group": "load-store",
	},
	"io.write": {
		"form": ["%i %r", "%i %n", "%i %q", "%i %f"],
		"writes": [],
		"group": "load-store",
	},
	"io.getc": {
		"form": ["%i", "%i %r"],
		"writes": [0],
		"group": "load-store",
	},
	"io.putc": {
		"form": ["%i %r", "%i %n"],
		"writes": [],
		"group": "load-store",
	},

	
	# branch
	"jmp": {
		"form": [
			"%i %r",
			"%i %n"
		],
		"writes": [],
		"group": "branch"
	},
	"br": {
		"form": [
			"%i %r %r",
			"%i %r %n",
		],
		"writes": [],
		"group": "branch"
	},
	"nbr": {
		"form": [
			"%i %r %r",
			"%i %r %n",
		],
		"writes": [],
		"group": "branch",
	},
	"call": {
		"form": [
			"%i %r",
			"%i %n"
		],
		"writes": [],
		"group": "branch"
	},
	"return": {
		"form": ["%i"],
		"writes": [],
		"group": "branch"
	},


	# logical (these are bitwise)
	"and": {
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		]
	},
	"or": {
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		]
	},
	"xor": {
		"form": [
			"%i %r %r %r",
			"%i %r %r %n",
		]
	},
	"not": {
		"form": [
			"%i %r %r",
			"%i %r %n",
		]
	},

	# # shift
	# "sl": {},
	# "sr": {},

	# simulator instructions
	"nop": {
		"form": ["%i"],
		"writes": [],
	},
	"halt": {
		"opcode": [0],
		"form": ["%i"],
		"writes": [],
		"group": "arithmetic",
		"cycles": 1,
		"width": 1,
		"blocking": True
	},
	"print": {
		"form": ["%i", "%i %r"]
	}

	# "": {},
}

rins = {0: "halt"}

def assign_opcodes():
	keys = sorted([k for k in ins.keys() if k != "halt"])

	counter = 1

	for key in keys:
		ins[key] = dict(defaults.items() + ins[key].items())

		ins[key]["opcode"] = []
		if "form" not in ins[key]:
			print "Error: All instructions must have atleast 1 form!"

		for s in ins[key]["form"]:
			ins[key]["opcode"].append(counter)
			rins[counter] = key
			counter += 1

		if counter > pow(2, 7):
			print "Error: Too many instructions to fit in the opcode!"
			return

# returns a field from an integer
def field(bytes, length, offset):
	return (bytes & ((1<<length)-1 << 64-offset-length)) >> 64-offset-length

# convert from twos complement to decimal
def twos_to_dec(num, bits=32):
	n = num & (1<<bits)-1
	return max( n if n < (2**bits)/2 else n-(2**bits), -(2**bits)/2)

# converts decimal to twos complement
def dec_to_twos(num, bits=32):
	return (num + (1 << bits)) % (1 << bits)

def float_to_bits(f):
	return struct.unpack('>l', struct.pack('>f', f))[0]

def bits_to_float(b):
	return struct.unpack('>f', struct.pack('>l', b))[0]

#*		Main - For testing really
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
if __name__ == "__main__":
	print "language testing"
	assign_opcodes()
	print "total number of instructions:",len(rins)

	# sys.stdout.write(json.dumps(ins, sort_keys=True, indent=4, separators=(',', ': ')))

	# print float_to_bits(100.0)

	# for k,i in zip(ins.keys(),ins.values()):
	# 	print k, i["opcode"]
	# 	# print bin(i["opcode"])