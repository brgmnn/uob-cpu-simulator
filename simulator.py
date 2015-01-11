#!/usr/bin/env python
import argparse, collections, Queue, json, os, sys
from StringIO import StringIO
import unit, language

language.assign_opcodes()

def _type(operand):
	if type(operand) is tuple:
		return operand[0]

def _reg(operand):
	if type(operand) is tuple and operand[0] == "reg":
		return operand[1]
	return None

#*		Memory class. Models memory such as ram.
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class Memory:
	def __init__(self, initialise=[]):
		self.ram = dict( zip(range(len(initialise)), initialise) )

	# reads from memory
	def __getitem__(self, addr):
		if type(addr) is int or type(addr) is long:
			# single byte addresses
			if addr in self.ram:
				return self.ram[addr]
			else:
				return 0
		elif type(addr) is slice:
			# slices of memory
			vals = []
			for i in range(addr.start, addr.stop+1):
				vals.append(format(self[i], "02x"))
			return int("".join(vals), 16)

	# writes to memory
	def __setitem__(self, addr, val):
		if type(addr) is int or type(addr) is long:
			# write a single byte
			self.ram[addr] = val
		elif type(addr) is slice:
			# write to a slice of memory
			vhex = format(val, "x")
			vhex = "0"+vhex if len(vhex) % 2 == 1 else vhex
			vals = [int("".join(x), 16) for x in zip(*[iter(vhex)]*2)]
			lens = len(vals) - len(range(addr.start, addr.stop+1))

			if lens > 0: 
				vals = vals[lens:]
			elif lens < 0:
				vals = [0 for i in range(-lens)]+vals

			for a, v in zip(range(addr.start, addr.stop+1), vals):
				self[a] = v

	def __str__(self):
		max_addr = max(self.ram.keys())
		fstr = str(len(str(max_addr)))+"d"
		skipstr = ("{0:^"+str(len(str(max_addr))+11)+"}").format("...")

		lmem = []
		zeroes = True
		dc = unit.Decode(None, None)

		for i in range(0, max(self.ram.keys())+1, 8):
			bytes = format(self[i:i+1], "04x")+" "+format(self[i+2:i+3], "04x") \
				+" "+format(self[i+4:i+5], "04x")+" "+format(self[i+6:i+7], "04x")

			if bytes != "0000 0000 0000 0000":
				lstr = format(i, fstr)+": "+bytes
				
				# if int(bytes.replace(" ", ""), 16) & 0xfe00000000000000 != 0:
				# 	ins = Instruction(bytes)
				# 	exc, ins = dc.decode(ins)
				# 	lstr += " "+str(ins)

				lmem.append(lstr)
				zeroes = False
			elif zeroes == False:
				lmem.append(skipstr)
				zeroes = True


		return " \n".join(lmem)

	def __repr__(self):
		lmem = zip(*[iter(self.ram.items())]*4)
		return " ".join([format(m[0][1], "02x")+format(m[1][1], "02x")+ \
			" "+format(m[2][1], "02x")+format(m[3][1], "02x") for m in lmem])

#*		Registers class. Models registers
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class Register:
	class NotFound(Exception):
		pass

	def __init__(self, **kwargs):
		arch = kwargs["architectural"] if "architectural" in kwargs else 128
		phys  = kwargs["physical"] if "physical" in kwargs else 128
		self.dchck = kwargs["dchck"] if "dchck" in kwargs else "queues"

		self.arch_size = arch
		self.size = phys

		self.iar = 0
		self.sp = -1

		# this is bad. the link register shouldnt be an epic stack
		self.lr = [] # the "link register" is actually a stack which assignment=push getting=pop
		self.reg = [0 for i in range(self.size)]
		self.regmap = {}
		self._reinitialise_scoreboard()
		

	def _reinitialise_scoreboard(self):
		if self.dchck == "scoreboard/queue":
			# scoreboarding using queues for each register on the scoreboard.
			self.sb = [[] for i in range(self.size)]
			self.lr_sb = []
			self.iar_sb = []
			self.sp_sb = []
		elif self.dchck == "scoreboard/renaming":
			# for the option of scoreboarding using bits with register renaming
			self.sb = [False for i in range(self.size)]
			self.lr_sb = False
			self.iar_sb = False
			self.sp_sb = False
			
			self.regmap = dict((i, i) for i in range(self.arch_size))
			self.tmp_regmap = dict((i, i) for i in range(self.arch_size))

	# gets a register
	def __getitem__(self, r):
		if type(r) is int or type(r) is long:
			return self.reg[r]
		elif r == "iar":
			return self.iar
		elif r == "lr":
			return self.lr.pop()
		elif r == "sp":
			return self.sp
		else:
			raise Register.NotFound

	# sets a register
	def __setitem__(self, r, val):
		if type(r) is int or type(r) is long:
			# val = val & 0xffffffff
			# self.reg[r] = val if val < (2**32)/2 else val-(2**32)
			if r < self.size/2:
				self.reg[r] = language.twos_to_dec(val)
			else:
				self.reg[r] = val
		elif r == "iar":
			# print " "*49,"-","iar =",val
			self.iar = val
		elif r == "lr":
			self.lr.append(val)
		elif r == "sp":
			self.sp = val
		else:
			raise Register.NotFound

	#*		Renaming
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def rename_lhs(self, ins):
		if ins.op[0] != None and ins.op[0][0] == "reg":
			ins.op[0] = ("reg", self.get_physical(_reg(ins.op[0])))

	def rename_rhs(self, ins):
		if ins.op[1] != None and ins.op[1][0] == "reg":
			ins.op[1] = ("reg", self.get_physical(_reg(ins.op[1])))
		if ins.op[2] != None and ins.op[2][0] == "reg":
			ins.op[2] = ("reg", self.get_physical(_reg(ins.op[2])))

	def remap(self, r):
		free = list(set([i for i in range(self.size) if not self.sb[i]]) - set(self.tmp_regmap.values()))
		# free = self.sb.index(False)
		# print free

		if len(free) > 0:
			phys = free[0]
			# print "renamed",r,":",self.tmp_regmap[r],"->",phys
			self.tmp_regmap[r] = phys
			return (r, phys)
		return (r, "bad rename!")
		# return -1

	def rollback_remaps(self):
		# print "rolled back renames!"
		self.tmp_regmap = self.regmap.copy()

	def commit_remaps(self, remaps):
		for r,phys in remaps:
			self.regmap[r] = phys

	def get_physical(self, r):
		return self.tmp_regmap[r] if self.dchck == "scoreboard/renaming" else r

	#*		Scoreboarding
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	# lock a register as it is changing
	def lock(self, r, iid):
		if r != None:
			if self.dchck == "scoreboard/queue":
				if type(r) is int or type(r) is long:
					self.sb[r].append(iid)
					self.sb[r].sort()
				elif r == "iar":
					self.iar_sb.append(iid)
					self.iar_sb.sort()
				elif r == "lr":
					self.lr_sb.append(iid)
					self.lr_sb.sort()
				elif r == "sp":
					self.sp_sb.append(iid)
					self.sp_sb.sort()
			elif self.dchck == "scoreboard/renaming":
				if type(r) is int or type(r) is long:
					self.sb[r] = True
				elif r == "iar":
					self.iar_sb = True
				elif r == "lr":
					self.lr_sb = True
				elif r == "sp":
					self.sp_sb = True
				# print "  locked register",r,"     iid =",iid

	# unlock a register as it is not being operated on anymore
	def unlock(self, r, iid):
		if r != None:
			if self.dchck == "scoreboard/queue":
				if type(r) is int or type(r) is long:
					self.sb[r].remove(iid)
				elif r == "iar":
					self.iar_sb.remove(iid)
				elif r == "lr":
					self.lr_sb.remove(iid)
				elif r == "sp":
					self.sp_sb.remove(iid)
			elif self.dchck == "scoreboard/renaming":
				if type(r) is int or type(r) is long:
					self.sb[r] = False
				elif r == "iar":
					self.iar_sb = False
				elif r == "lr":
					self.lr_sb = False
				elif r == "sp":
					self.sp_sb = False
				# print "unlocked register",r,"     iid=",iid

	# flush the scoreboarding system
	def flush(self):
		if self.dchck == "scoreboard/queue":
			# this is also bad
			self.sb = [[] for i in range(self.size)]
			self.lr_sb = []
			self.iar_sb = []
			self.sp_sb = []
		elif self.dchck == "scoreboard/renaming":
			# undo all in transit renames
			self.rollback_remaps()
			self.sb = [False for i in range(self.size)]
			self.lr_sb = False
			self.iar_sb = False
			self.sp_sb = False

	def isfreearch(self, r, iid):
		if type(r) is int or type(r) is str:
			return self.isfree(self.get_physical(r), iid)
		return True

	def isfree(self, r, iid):
		if self.dchck == "scoreboard/queue":
			if type(r) is int or type(r) is long:
				return min(self.sb[r]+[9999999999999999]) >= iid
			elif r == "iar":
				return min(self.iar_sb+[9999999999999999]) >= iid
			elif r == "lr":
				return min(self.lr_sb+[9999999999999999]) >= iid
			elif r == "sp":
				return min(self.sp_sb+[9999999999999999]) >= iid
		elif self.dchck == "scoreboard/renaming":
			if type(r) is int or type(r) is long:
				return not self.sb[r]
			elif r == "iar":
				return not self.iar_sb
			elif r == "lr":
				return not self.lr_sb
			elif r == "sp":
				return not self.sp_sb
		return True

	#*		Output
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def __str__(self):
		s = "iar="+str(self.iar)+", lr="+str(self.lr)+", sp="+str(self.sp)+"\n  integer=" \
			+str([int(self[self.get_physical(i)]) for i in range(self.size/2)])+"\n    float=" \
			+str([float(self[self.get_physical(i)]) for i in range(self.size/2, self.size)])

		if self.dchck == "scoreboard/renaming":
			s += "\n       physical="+str(self.reg)+"\n        mapping="+str(self.regmap)

		return s

	def __repr__(self):
		return "regs="+str([self[self.get_physical(i)] for i in range(self.arch_size)])

#*		Instruction class
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
def str_op(op):
	if type(op) is tuple:
		val = op[1]
		if type(val) == str:
			# for special registers like iar / lr.
			return val
		# elif type(val) 

		if op[0] == "reg":
			if val < language.registers/2:
				return "r"+str(val)
			else:
				return "q"+str(val-(language.registers/2))
		elif op[0] == "int":
			return "#"+str(val)
		elif op[0] == "float":
			return "#"+str(val)
		elif op[0] == "mem":
			return "m["+str_op(val)+"]"
		else:
			return str(val)
	elif type(op) is int or type(op) is long or type(op) is float:
		return str(op)
	return ""

class Instruction:
	pad = {"id": 5, "opcode": 6, "delta-offset": 21, "reg-lhs": 3}

	def __init__(self, *args, **kwargs):
		self.id = kwargs["id"] if "id" in kwargs else -1
		self.bytes = None
		self.opcode = None
		self.lex = ""
		self.form = ""
		self.op = []
		self.opr = None
		self.opa = None
		self.opb = None
		self.iar = kwargs["iar"] if "iar" in kwargs else None
		self.renames = []
		self.brtaken = False
		self._update(args, kwargs)
		self.delta = []

	def update(self, *args, **kwargs):
		self._update(args, kwargs)
		return self

	def _update(self, args, kwargs):
		if len(args) == 1:
			if type(args[0]) is str:
				self.bytes = int(args[0].replace(" ", ""), 16)
			elif type(args[0]) is int or type(args[0]) is long:
				self.bytes = args[0]
			elif type(args[0]) is dict:
				d = args[0]
				self.opcode = d["opcode"]
				self.opr = d["opr"]
				self.opa = d["opa"]
				self.opb = d["opb"]

		if "iar" in kwargs:
			self.iar = kwargs["iar"]

	def legacy_form(self):
		return {"opcode": self.opcode, "opr": self.opr, "opa": self.opa, "opb": self.opb}

	def __str__(self):
		if self.opcode != None:
			if len(self.delta) > 0:
				sd = " -> "
				changes = []
				for d in self.delta:
					changes.append(("{0:<12}").format(("{0:>5}").format(str_op(d[0]))+"="+str_op(d[1])))
				sd += " ".join(changes)
			else:
				sd = ""

			# ops = [s for s in [str_op(self.opr), str_op(self.opa), str_op(self.opb)] if s != ""]
			ops = ",".join([str_op(op) for op in self.op])
			# print self.op
			iar = ("{0:>8}").format("x"+format(self.iar, "x")) if type(self.iar) is int else ""

			return ("{0:>8}").format(self.id)+" "+iar+": "+("{0:<25}").format( \
				("{0:>10}").format(self.lex)+" "+ops)+("{0:<20}").format(sd)
				# +("{:<10}").format(",".join(["r"+str(rn[0])+" -> "+"r"+str(rn[1]) for rn in self.renames]))
		else:
			return hex(self.bytes)

	def __repr__(self):
		return "<"+str(self.id)+": "+str(self.lex)+" "+",".join([str_op(o) for o in self.op]) \
			+" - "+str(self.iar)+">"

#*		The simulator. Runs code.
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class Simulator:
	#*		Initialiser
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def __init__(self, path, numregs=128):
		# instruction address register. this is the last (highest numbered) register.

		self.settings = {
			"pipelined": False,
			"n-way": 1,
			"execution units": {
				"arithmetic": 1,
				"vector-arithmetic": 1,
				"load-store": 1,
				"branch": 1
			},
			"branch prediction": {
				"type": "off",
				"history length": 4,
				"states": 4
			},
			"dependancies": "scoreboard/queue",
			"renaming": False,
			"register renaming": False,
			"log": True,
			"ins-log": True
		}

		fp = open(path, "r")
		self.exe_path = path
		self.memory = Memory([int(byte, 16) for byte in fp.read().split()])
		self.register = Register( architectural=numregs, dchck=self.settings["dependancies"] )

		self.components = []
		self.ilog = []

		self.io_in = ""
		self.io_out = sys.stdout

		self.clk = 0
		self.sum_ins = 0
		self.open_settings()

	#*		Settings
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def open_settings(self):
		try:
			values = json.load(open("settings.json", "rb"))
			self.settings = dict(self.settings.items() + values.items())
			self.register.dchck = self.settings["dependancies"]
			self.register._reinitialise_scoreboard()
		except IOError:
			print >> sys.stderr, "Error: Failed to open the settings files. Attempting to create \
				it now..."
			try:
				open("settings.json", "wb").write(json.dumps(self.settings, sort_keys=True, \
					indent=4, separators=(',', ': ')))
			except IOError:
				print >> sys.stderr, "Error: Failed to save settings."
		return self.settings

	#*		Debugging
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def dump(self):
		print "  State dump"
		print "registers:",self.register
		print "memory:   ",str(self.memory).replace("\n", "\n           ")

	def generate_test_reference(self):
		print self.exe_path
		tdir = os.path.dirname(self.exe_path)
		name = os.path.splitext( os.path.basename(self.exe_path) )
		basepath = os.path.join( tdir, name[0] )

		fpr = open(basepath+".reg", "w")
		fpm = open(basepath+".mem", "w")
		
		fpr.write(repr(self.register))
		fpm.write(repr(self.memory))

		print fpr, fpm

	def load_input(self, path):
		with open(path, "r") as content:
			self.io_in = content.read()

	#*		Run function
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def run(self):
		ft = unit.Fetch(self)
		dc = unit.Decode(self, ft)
		self.components.append([ft])
		self.components.append([dc])

		rs_ar  = unit.ReservationStation(self, dc, "arithmetic")
		rs_var = unit.ReservationStation(self, dc, "vector-arithmetic")
		rs_ls  = unit.ReservationStation(self, dc, "load-store")
		rs_br  = unit.ReservationStation(self, dc, "branch")
		self.components.append([rs_ar, rs_var, rs_ls, rs_br])

		ar  = [unit.Arithmetic(self, rs_ar) for i in \
			range(self.settings["execution units"]["arithmetic"])]
		var = [unit.VectorArithmetic(self, rs_var) for i in \
			range(self.settings["execution units"]["vector-arithmetic"])]
		ls  = [unit.LoadStore(self, rs_ls) for i in \
			range(self.settings["execution units"]["load-store"])]
		br  = [unit.Branch(self, rs_br) for i in range(self.settings["execution units"]["branch"])]
		self.components.append(ar + var + ls + br)

		rb = unit.ReorderBuffer(self, [ar, var, ls, br])
		rb.link_idbus(dc) # link the id bus between the decoder and reorder buffer.		
		wb = unit.WriteBack(self, rb, ft)
		wb.link_fetch(ft)
		log = unit.Log(self, wb)
		self.components.append([rb])
		self.components.append([wb])
		self.components.append([log])

		# print rb.ibus

		unit.Unit.components = self.components

		while not log.halt:
		# for i in range(10):
			if self.settings["pipelined"] == True:
				# for a pipelined simulator. clock all units then shift all units
				for stage in self.components:
					for u in stage:
						u.clk()
				for stage in self.components:
					for u in stage:
						u.shift()
			else:
				# non pipelined. each unit is clocked and immediately outputs for the next unit
				for stage in self.components:
					for u in stage:
						u.clk()
						u.shift()

			# print "param:",sum(len(x) for x in self.register.sb),len(self.register.iar_sb),len(self.register.sp_sb),len(self.register.lr_sb)
			# print "iar sb:",self.register.iar_sb
			# raw_input("stage...")

			# print self.register.sb[:5]
			# print "-"*100
			# raw_input()

		print log

#*		Main
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
if __name__ == "__main__":
	ap = argparse.ArgumentParser(description="SuperScalar simulator")
	ap.add_argument("program",
		type=str,
		help="Program to load and run.")
	ap.add_argument("--generate-test-data",
		action="store_true",
		dest="gentest",
		help="Generates the necessary test data for unit testing. Warning! Be sure the program is \
			working correctly before generating this!")
	ap.add_argument("--io-input", "-in",
		type=str,
		dest="io_input",
		metavar=("FILE"),
		help="Input file for the simulators io to read from.")
	ap.add_argument("--io-output", "-out",
		type=str,
		dest="io_output",
		metavar=("FILE"),
		help="Input file for the simulators io to read from.")

	args = ap.parse_args()

	# print
	sim = Simulator(args.program)
	sim.open_settings()

	if args.io_input:
		# print args.io_input
		sim.load_input(args.io_input)
	if args.io_output:
		# print args.io_output
		sim.io_out = open(args.io_output, "w")
	if args.gentest:
		sys.stdout = open("/dev/null", "w")

	sim.run()

	if args.gentest:
		sim.generate_test_reference()
	else:
		pass
		sim.dump()
