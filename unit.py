#!/usr/bin/env python
import Queue, collections
from simulator import Instruction
import language

language.assign_opcodes()

class FlushPipeline(Exception):
	pass

def _type(operand):
	if type(operand) is tuple:
		return operand[0]

def _reg(operand, offset=0):
	if type(operand) is tuple and operand[0] == "reg":
		return operand[1]+offset
	return None

#*		Unit class
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
# unit interface class
class Unit(object):
	components = [[]]

	@staticmethod
	def flush_all():
		for stage in Unit.components:
			for u in stage:
				u.flush()

	def __init__(self, sim=None, ounit=None):
		self.ibus = collections.deque()
		if ounit != None:
			ounit.link_out_to(self)
			ounit.iunit = self
		if sim != None:
			self.settings = sim.settings
			self.register = sim.register
		self.obus = collections.deque()
		self.buffer = []
		self.blocking = 0

	def _reg(self, operand):
		if type(operand) is tuple and operand[0] == "reg":
			return operand[1]
		return None

	def _val(self, operand, reg_offset=0):
		if type(operand) is tuple:
			if operand[0] == "reg" and type(operand[1]) is int or type(operand[1]) is long:
				return self.register[operand[1]+reg_offset]
			elif operand[0] in ["int", "imm", "fload"]:
				return operand[1]
			elif operand[0] == "reg" and type(operand[1]) is str:
				return self.register[operand[1]]
		elif type(operand) is int or type(operand) is long:
			return operand
		return 0

	# links our output queue to their input queue
	def link_out_to(self, u):
		if issubclass(type(u), Unit):
			self.obus = u.ibus

	# links our input queue to their output queue
	def link_in_from(self, u):
		if issubclass(type(u), Unit):
			self.ibus = u.obus

	def clk(self):
		pass

	def shift(self):
		for i in range(self.settings["n-way"]):
			try:
				self.obus.appendleft(self.buffer[i])
			except IndexError:
				pass

	# flush the units current buffer
	def flush(self):
		self.buffer = []
		self.obus.clear()


#*		Decode unit
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class Fetch(Unit):
	def __init__(self, sim):
		super(Fetch, self).__init__(sim)
		self.ins_count = 0
		self.memory = sim.memory
		self.register = sim.register
		self.buffer = []
		self.br_decoder = Decode(None, None)
		self.settings = sim.settings
		self.halt = False
		self.stalled = False
		self.brcache = {}

		self.pattern_table = {}
		self.counter_table = {}


	def clk(self):
		addr = self.register["iar"]
		self.buffer = []

		# if not self.halt:
		if len(self.register.iar_sb) < 4*self.settings["n-way"]:
			for i in range(self.settings["n-way"]):
				ins = Instruction( self.memory[addr:addr+7], iar=addr, id=self.next_iid() )
				ins.iar = addr

				if not self.stalled:
					self.buffer.append( ins )

				# exe, ins = self.br_decoder.decode(ins)
				# print addr,ins
				# print self.register.lr

				ins.opcode = language.field(ins.bytes, 7, 0)
				ins.lex = language.rins[ins.opcode]
				# print repr(ins)

				if ins.lex in ["jmp", "br", "nbr", "call", "return"]:
					addr = self.branch_predictor(ins)
					if self.stalled == True:
						# print "fetch unit stalled on return instruction."
						break
				elif ins.lex == "halt":
					# self.halt = True
					self.stalled = True
					break
				else:
					addr += 8

		# raw_input("fetched...")
		self.register["iar"] = addr

	def next_iid(self):
		self.ins_count += 1
		return self.ins_count

	def flush(self):
		super(Fetch, self).flush()
		self.halt = False
		self.stalled = False

	#*		Branch prediction
	#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
	def branch_predictor(self, ins):
		Decode._operands(ins)
		if self.settings["branch prediction"]["type"] == "always take":
			if ins.lex in ["jmp", "call"] and _type(ins.op[0]) == "int":
				ins.brtaken = True
				ins.brto = ins.op[0][1]
				return ins.op[0][1]
			elif ins.lex in ["br", "nbr"] and _type(ins.op[1]) == "int":
				ins.brtaken = True
				ins.brto = ins.op[1][1]
				return ins.op[1][1]
			elif ins.lex == "return":
				ins.brtaken = False
				self.stalled = True
				ins.brto = ins.iar+8
				return ins.iar + 8

		elif self.settings["branch prediction"]["type"] == "dynamic local":
			if ins.lex in ["jmp", "call"] and _type(ins.op[0]) == "int":
				ins.brtaken = True
				ins.brto = ins.op[0][1]
				return ins.op[0][1]
			elif ins.lex in ["br", "nbr"] and _type(ins.op[1]) == "int":
				# print ins.iar,self.get_history(ins.iar),self.get_counter(ins.iar)
				if self.get_counter(ins.iar) < self.settings["branch prediction"]["states"]/2:
					ins.brtaken = False
					ins.brto = ins.iar + 8
					return ins.iar + 8
				else:
					ins.brtaken = True
					ins.brto = ins.op[1][1]
					return ins.op[1][1]
			elif ins.lex == "return":
				if ins.iar in self.brcache:
					# print "found in cache",self.brcache[ins.iar],ins.iar
					ins.brtaken = True
					ins.brto = self.brcache[ins.iar]
					return self.brcache[ins.iar]
				else:
					ins.brtaken = False
					self.stalled = True
					ins.brto = ins.iar + 8
					return ins.iar + 8
		else:
			ins.brtaken = False

		ins.brto = ins.iar + 8
		return ins.iar + 8

	def get_history(self, iar):
		history = self.pattern_table[iar] if iar in self.pattern_table else \
			"".join(["1" for i in range(self.settings["branch prediction"]["history length"])])

		if iar not in self.pattern_table:
			self.pattern_table[iar] = history

		return history

	def get_counter(self, iar):
		history = self.get_history(iar)
		counter = self.counter_table[iar,history] if (iar,history) in self.counter_table else \
			self.settings["branch prediction"]["states"]/2

		if (iar,history) not in self.counter_table:
			self.counter_table[iar,history] = counter

		return counter

	def update_predictor(self, iar, brto, result):
		self.brcache[iar] = brto
		history = self.get_history(iar)
		counter = self.get_counter(iar)
		if result:
			self.counter_table[iar,history] = min(self.settings["branch prediction"]["states"], \
				counter+1)
			self.pattern_table[iar] = "1"+history[1:]
		else:
			self.counter_table[iar,history] = max(0, counter-1)
			self.pattern_table[iar] = "0"+history[1:]

	def shift(self):
		super(Fetch, self).shift()

#*		Decode unit
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
# this unit will also issue instructions
class Decode(Unit):
	def __init__(self, sim, ufetch=None):
		super(Decode, self).__init__(sim, ufetch)
		self.obus = {
			"arithmetic": collections.deque(),
			"vector-arithmetic": collections.deque(),
			"load-store": collections.deque(),
			"branch": collections.deque()
		}
		if sim != None:
			self.register = sim.register
		self.idbus = collections.deque()
		self.buffer = None

	# as we have multiple outputs we need an overridden link_out_to() function.
	def link_out_to(self, u):
		if issubclass(type(u), Unit):
			if type(u) is Arithmetic or (hasattr(u, "preceeds") and u.preceeds == "arithmetic"):
				self.obus["arithmetic"] = u.ibus
			if type(u) is VectorArithmetic or (hasattr(u, "preceeds") and u.preceeds == "vector-arithmetic"):
				self.obus["vector-arithmetic"] = u.ibus
			elif type(u) is LoadStore or (hasattr(u, "preceeds") and u.preceeds == "load-store"):
				self.obus["load-store"] = u.ibus
			elif type(u) is Branch or (hasattr(u, "preceeds") and u.preceeds == "branch"):
				self.obus["branch"] = u.ibus

	def clk(self):
		self.buffer = []
		for i in range(self.settings["n-way"]):
			try:
				ins = self.ibus.pop()
				self.buffer.append( self.decode(ins) )
			except IndexError:
				pass

	def shift(self):
		# print self.register.sb[:10],self.register.sp_sb,self.register.iar_sb
		for i in range(self.settings["n-way"]):
			try:
				u, ins = self.buffer[i]
				self.obus[u].appendleft(ins)
				self.idbus.appendleft(ins.id)

				if self.settings["dependancies"] == "scoreboard/renaming":
					self.register.rename_rhs(ins)

					if not self.register.isfreearch(_reg(ins.op[0]), ins.id):
						renames = self.register.remap(_reg(ins.op[0]))
						ins.renames.append(renames)
					
					# print "-".join(["1" if b else "0" for b in self.register.sb])
					self.register.rename_lhs(ins)
					# print ins

				#print "decode:",repr(ins)

				for w in language.ins[ins.lex]["writes"]:
					for i in range(language.ins[ins.lex]["width"]):
						self.register.lock(_reg(ins.op[w], i), ins.id)
						# print "locking r"+str(_reg(ins.op[w], i))

				if ins.lex in ["jmp", "br", "nbr", "call", "return"]:
					self.register.lock("iar", ins.id)

				if ins.lex in ["push", "pop", "spr", "call", "return"]:
					self.register.lock("sp", ins.id)

			except IndexError:
				pass

	def flush(self):
		self.buffer = []
		self.idbus.clear()
		for k, bus in self.obus.iteritems():
			bus.clear()

	def decode(self, ins):
		ins.opcode = language.field(ins.bytes, 7, 0)
		ins.lex = language.rins[ins.opcode]
		lang = language.ins[ins.lex]
		ins.form = lang["form"][lang["opcode"].index(ins.opcode)].split()
		
		op = []
		for i,f in zip(range(len(ins.form)), ins.form):
			if i > 0:
				if f == "%r":
					op.append(("reg", language.field(ins.bytes,7,7*i)))
				elif f == "%q":
					op.append(("reg", language.field(ins.bytes,7,7*i)))
				elif f == "%n":
					op.append(("int", language.twos_to_dec(language.field(ins.bytes,64-(7*i),7*i))))
				elif f == "%f":
					op.append(("float", language.bits_to_float(language.field(ins.bytes,32,7*i))))

		ins.op = op
		# print ins
		return lang["group"], ins

	@staticmethod
	def _operands(ins):
		lang = language.ins[ins.lex]
		ins.form = lang["form"][lang["opcode"].index(ins.opcode)].split()

		op = []
		for i,f in zip(range(len(ins.form)), ins.form):
			if i > 0:
				if f == "%r":
					op.append(("reg", language.field(ins.bytes,7,7*i)))
				elif f == "%n":
					op.append(("int", language.twos_to_dec(language.field(ins.bytes,64-(7*i),7*i))))

		ins.op = op

#*		Reservation Station
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
# ensures that instructions are held until their operands are unchanging
class ReservationStation(Unit):
	def __init__(self, sim, uprev, preceeds):
		self.preceeds = preceeds
		super(ReservationStation, self).__init__(sim, uprev)
		self.register = sim.register
		# self.buffer = collections.deque()
		self.buffer = []
		self.obus = []

	def clk(self):
		for i in range(self.settings["n-way"]):
			try:
				ins = self.ibus.pop()
				self.buffer.append(ins)
			except IndexError:
				pass
		# print self.preceeds,self.buffer

	# links our output queue to their input queue. each reservation station can serve many execution
	# units
	def link_out_to(self, u):
		if issubclass(type(u), Unit):
			self.obus.append(u.ibus)

	def shift(self):
		# print self.preceeds+":",self.buffer
		for bus in self.obus:
			for i in self.buffer:

				freelist = []

				if type(language.ins[i.lex]["width"]) is int:
					for v in range(language.ins[i.lex]["width"]):
						freelist.extend([self.register.isfree(_reg(i.op[c],v), i.id) for c in \
							list(set(range(len(i.op))) - set(language.ins[i.lex]["writes"]))])
				elif type(language.ins[i.lex]["width"]) is list:
					for op in list(set(range(len(i.op))) - set(language.ins[i.lex]["writes"])):
						freelist.extend([self.register.isfree(_reg(i.op[op],v), i.id) for v in \
							range(language.ins[i.lex]["width"][op])])

					# for v in language.ins[i.lex]["width"]:
					# 	freelist.extend([self.register.isfree(_reg(i.op[c],v), i.id) for c in \
					# 		list(set(range(len(i.op))) - set(language.ins[i.lex]["writes"]))])

				# print repr(i),self.iunit.busy,freelist

				if False not in freelist and not self.iunit.busy:
					bus.appendleft(i)
					self.buffer.remove(i)
					break
				else:
					pass
					# print "stalled instruction"

		# print self.preceeds,self.buffer
		self.served = [False for i in range(len(self.obus))]
		# print self.buffer

	# flush the units current buffer
	def flush(self):
		self.buffer = []
		for bus in self.obus:
			bus.clear()

#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
#*
#*		Execution units!
#*
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class Execution(Unit):
	def __init__(self, sim, udecode=None):
		super(Execution, self).__init__(sim, udecode)
		self.register = sim.register
		self.memory = sim.memory
		self.buffer = None
		self.busy = False
		self.cycles_remaining = 0

	def _val(self, operand, reg_offset=0):
		if operand[0] == "reg":
			return self.register[operand[1]+reg_offset]
		elif operand[0] in ["int", "imm", "float"]:
			return operand[1]
		else:
			return 0

	def _reg(self, operand):
		if type(operand) is tuple and operand[0] == "reg":
			return operand[1]
		return None

	def clk(self):
		# print "        "+self.__class__.__name__+" unit:",self.busy,repr(self.buffer)
		if not self.busy:
			try:
				ins = self.ibus.pop()
				getattr(self, "_"+ins.lex.replace(".", ""))(ins)
				self.buffer = ins
				self.cycles_remaining = language.ins[ins.lex]["cycles"] - 1
				self.busy = True
			except IndexError as e:
				self.buffer = None

	def shift(self):
		if self.buffer != None and self.cycles_remaining <= 0:
			self.obus.appendleft(self.buffer)
			self.busy = False
		elif self.buffer != None and self.cycles_remaining > 0:
			self.cycles_remaining -= 1
		else:
			# the unit isnt busy, allow it to be used for other instructions
			self.busy = False
			self.buffer = None

	def flush(self):
		self.buffer = None
		self.obus.clear()

class Arithmetic(Execution):
	def __init__(self, sim, udecode=None):
		super(Arithmetic, self).__init__(sim, udecode)

	def _mov(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1])))

	def _add(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) + self._val(ins.op[2])))

	def _sub(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) - self._val(ins.op[2])))

	def _mul(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) * self._val(ins.op[2])))

	def _div(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) / self._val(ins.op[2])))

	def _mod(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) % self._val(ins.op[2])))

	def _shl(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) << self._val(ins.op[2])))

	def _shr(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) >> self._val(ins.op[2])))

	def _gt(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), \
			1 if self._val(ins.op[1]) > self._val(ins.op[2]) else 0))

	def _gte(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), \
			1 if self._val(ins.op[1]) >= self._val(ins.op[2]) else 0))

	def _eq(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), \
			1 if self._val(ins.op[1]) == self._val(ins.op[2]) else 0))

	def _and(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) & self._val(ins.op[2])))
		
	def _or(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) | self._val(ins.op[2])))

	def _xor(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), self._val(ins.op[1]) ^ self._val(ins.op[2])))

	def _not(self, ins):
		ins.delta.append((("reg", ins.op[0][1]), ~self._val(ins.op[1])))

	def _nop(self, ins):
		pass

	def _print(self, ins):
		pass

	def _pause(self, ins):
		raw_input("Execution paused. Press Enter to continue...")

	def _halt(self, ins):
		pass

class VectorArithmetic(Execution):
	def __init__(self, sim, udecode=None):
		super(VectorArithmetic, self).__init__(sim, udecode)

	def _vmov(self, ins):
		ins.delta.append((("reg", ins.op[0][1]  ), self._val(ins.op[1]  )))
		ins.delta.append((("reg", ins.op[0][1]+1), self._val(ins.op[1],1)))
		ins.delta.append((("reg", ins.op[0][1]+2), self._val(ins.op[1],2)))
		ins.delta.append((("reg", ins.op[0][1]+3), self._val(ins.op[1],3)))

	def _vadd(self, ins):
		ins.delta.append((("reg", ins.op[0][1]  ), self._val(ins.op[1]  ) + self._val(ins.op[2]  )))
		ins.delta.append((("reg", ins.op[0][1]+1), self._val(ins.op[1],1) + self._val(ins.op[2],1)))
		ins.delta.append((("reg", ins.op[0][1]+2), self._val(ins.op[1],2) + self._val(ins.op[2],2)))
		ins.delta.append((("reg", ins.op[0][1]+3), self._val(ins.op[1],3) + self._val(ins.op[2],3)))

	def _vsub(self, ins):
		ins.delta.append((("reg", ins.op[0][1]  ), self._val(ins.op[1]  ) - self._val(ins.op[2]  )))
		ins.delta.append((("reg", ins.op[0][1]+1), self._val(ins.op[1],1) - self._val(ins.op[2],1)))
		ins.delta.append((("reg", ins.op[0][1]+2), self._val(ins.op[1],2) - self._val(ins.op[2],2)))
		ins.delta.append((("reg", ins.op[0][1]+3), self._val(ins.op[1],3) - self._val(ins.op[2],3)))

	def _vmul(self, ins):
		ins.delta.append((("reg", ins.op[0][1]  ), self._val(ins.op[1]  ) * self._val(ins.op[2]  )))
		ins.delta.append((("reg", ins.op[0][1]+1), self._val(ins.op[1],1) * self._val(ins.op[2],1)))
		ins.delta.append((("reg", ins.op[0][1]+2), self._val(ins.op[1],2) * self._val(ins.op[2],2)))
		ins.delta.append((("reg", ins.op[0][1]+3), self._val(ins.op[1],3) * self._val(ins.op[2],3)))

	def _vdiv(self, ins):
		ins.delta.append((("reg", ins.op[0][1]  ), self._val(ins.op[1]  ) / self._val(ins.op[2]  )))
		ins.delta.append((("reg", ins.op[0][1]+1), self._val(ins.op[1],1) / self._val(ins.op[2],1)))
		ins.delta.append((("reg", ins.op[0][1]+2), self._val(ins.op[1],2) / self._val(ins.op[2],2)))
		ins.delta.append((("reg", ins.op[0][1]+3), self._val(ins.op[1],3) / self._val(ins.op[2],3)))

	def _vmod(self, ins):
		ins.delta.append((("reg", ins.op[0][1]  ), self._val(ins.op[1]  ) % self._val(ins.op[2]  )))
		ins.delta.append((("reg", ins.op[0][1]+1), self._val(ins.op[1],1) % self._val(ins.op[2],1)))
		ins.delta.append((("reg", ins.op[0][1]+2), self._val(ins.op[1],2) % self._val(ins.op[2],2)))
		ins.delta.append((("reg", ins.op[0][1]+3), self._val(ins.op[1],3) % self._val(ins.op[2],3)))

class LoadStore(Execution):
	def __init__(self, sim, udecode=None):
		super(LoadStore, self).__init__(sim, udecode)

	def _load(self, ins):
		ins.delta.append((("reg", self._reg(ins.op[0])), \
			self.memory[self._val(ins.op[1]):self._val(ins.op[1])+3]))
		# print self._val(ins.op[1])

	def _store(self, ins):
		# self.memory[self._val(ins.op[1]):self._val(ins.op[1])+3] = language.dec_to_twos(self.register[self._reg(ins.op[0])])
		# ins.delta.append(( ("mem", ins.op[1]), language.dec_to_twos(self.register[self._reg(ins.op[0])]) ))
		ins.delta.append(( ("mem", ins.op[1]), ins.op[0] ))

	# stack operations: push, pop and set the stack pointer
	def _push(self, ins):
		# ins.delta.append(( ("mem", ("reg", "sp")), self._val(ins.op[0]) ))
		ins.delta.append(( ("mem", ("reg", "sp")), ins.op[0] ))
		ins.delta.append(( ("reg", "sp"),  4))

	def _pop(self, ins):
		ins.delta.append(( ("reg", "sp"), -4))
		ins.delta.append(( ("reg", ins.op[0][1]), ("mem", "sp") ))

	def _spr(self, ins):
		ins.delta.append(( "spw", ins.op[0][1] ))

	def _ioread(self, ins):
		ins.delta.append(( ins.op[0], ("io", "in") ))

	def _iowrite(self, ins):
		ins.delta.append(( ("io", "out"), ins.op[0] ))

	def _iogetc(self, ins):
		ins.delta.append(( ins.op[0], ("io", "in-ascii") ))

	def _ioputc(self, ins):
		ins.delta.append(( ("io", "out-ascii"), ins.op[0] ))

class Branch(Execution):
	def __init__(self, sim, udecode=None):
		super(Branch, self).__init__(sim, udecode)

	def _jmp(self, ins):
		ins.delta.append((("reg", "iar"), self._val(ins.op[0])))

	def _br(self, ins):
		if self._val(ins.op[0]) > 0:
			ins.delta.append((("reg", "iar"), self._val(ins.op[1])))

	def _nbr(self, ins):
		if self._val(ins.op[0]) == 0:
			ins.delta.append((("reg", "iar"), self._val(ins.op[1])))

	def _call(self, ins):
		ins.delta.append((("reg", "iar"), self._val(ins.op[0])))
		ins.delta.append(( ("mem", ("reg", "sp")), ins.iar+8 ))
		ins.delta.append(( ("reg", "sp"),  4))

	def _return(self, ins):
		ins.delta.append(( ("reg", "sp"), -4))
		ins.delta.append(( ("reg", "iar"), ("mem", "sp") ))


#*		Reorder buffer
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class ReorderBuffer(Unit):
	def __init__(self, sim, uexecs=[]):
		super(ReorderBuffer, self).__init__(sim)
		self.sim = sim
		self.ibus = [u.obus for classes_of_exec in uexecs for u in classes_of_exec]
		self.buffer = []
		self.register = sim.register
		self.idbus = None
		self.lastid = 0

	# the reorder buffer has to accept streams in from multiple execution units.
	def link_in_from(self, u):
		if issubclass(type(u), Unit):
			self.ibus.append(u.obus)

	def link_idbus(self, dc):
		self.idbus = dc.idbus

	def clk(self):
		# dont need to loop by n-ways as this checks every output buffer
		for bus in self.ibus:
			try:
				ins = bus.pop()
				self.buffer.append(ins)
			except IndexError:
				pass
		# print self.buffer

		# sort the instructions by their id
		self.buffer.sort(key=lambda ins: ins.id)

	def _iid(self, iid):
		for ins in self.buffer:
			if ins.id == iid:
				return ins
		raise IndexError

	def shift(self):
		# print "rb:",sorted(self.idbus),self.buffer

		for i in range(self.settings["n-way"]):
			for iid in sorted(self.idbus):
				found = False
				try:
					ins = self._iid(iid)
					self.obus.appendleft(ins)
					self.idbus.pop()
					self.buffer.remove(ins)
				except IndexError:
					break

		# for ins in self.buffer:
		# 	self.obus.appendleft(ins)
		# self.buffer = []

	def flush(self):
		self.buffer = []
		self.obus.clear()

#*		Write back unit. Writes the changes back to the registers
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
class WriteBack(Unit):
	def __init__(self, sim, upre=None, fetchunit=None):
		super(WriteBack, self).__init__(sim, upre)
		self.buffer = []
		self.register = sim.register
		self.memory = sim.memory
		self.next_iar = 0
		self.halt_buffer = []
		self.sim = sim
		self.fetch = fetchunit
		self.io_in = sim.io_in
		self.io_out = sim.io_out

	def clk(self):
		while True:
			try:
				ins = self.ibus.pop()
				# print ins
				self.buffer.append(ins)
			except IndexError:
				break

		# print self.register[0], self.register[1], self.register[2], self.register[3]
		# print self.buffer

		hit_branch = False
		for ins in self.buffer:
			regops = [x[0][1] for x in ins.delta]

			for d in ins.delta:
				if d[0][0] == "reg" and d[0][1] != "iar" and d[0][1] != "sp":
					# write the change to the register if it is not a change to the iar or stack
					# pointer.
					if type(d[1]) is tuple and d[1][0] == "mem":
						# reading from memory
						if type(d[1][1]) is int or type(d[1][1]) is long:
							self.register[d[0][1]] = self.memory[d[1][1]:d[1][1]+3]
						elif d[1][1] == "sp":
							# this only happens in pop instructions.
							self.register[d[0][1]] = \
								self.memory[self.register["sp"]:self.register["sp"]+3]
					elif type(d[1]) is tuple and d[1][0] == "io":
						if d[1][1] == "in":
							val = self.io_read(d[0])
							if val != None:
								# print val
								self.register[d[0][1]] = val
						elif d[1][1] == "in-ascii":
							c = self.io_getc()
							if val != -1:
								self.register[d[0][1]] = c
					else:
						self.register[d[0][1]] = d[1]
				elif d[0][0] == "io":
					if d[0][1] == "out":
						self.io_out.write(str(self._val(d[1])))
					elif d[0][1] == "out-ascii":
						self.io_out.write(chr(self._val(d[1])))
				elif d[0][0] == "mem":
					# writing to memory
					self.memory[self._val(d[0][1]):self._val(d[0][1])+3] = language.dec_to_twos(self._val(d[1]))
				elif d[0] == "spw":
					# directly write a value to the stack pointer register
					self.register["sp"] = d[1]
				elif d[0] == ("reg", "sp"):
					# move the stack pointer register up or down the stack
					self.register["sp"] += d[1]
					

			self.obus.appendleft(ins)

			for w in language.ins[ins.lex]["writes"]:
				for i in range(language.ins[ins.lex]["width"]):
					self.register.unlock(_reg(ins.op[w], i), ins.id)
					# print "unlocking r"+str(_reg(ins.op[w], i))

			if ins.lex in ["jmp", "br", "nbr", "call", "return"]:
				self.register.unlock("iar", ins.id)

			if ins.lex in ["push", "pop", "spr", "call", "return"]:
				self.register.unlock("sp", ins.id)



			# checks if the branch prediction was successful
			if ins.brtaken != ("iar" in regops) or ins.lex == "return":
				# print "flushing pipeline :("
				# not successful in taking the branch
				if "iar" in regops:
					for d in ins.delta:
						if d[0] == ("reg", "iar"):
							if type(d[1]) is tuple and d[1][0] == "mem":
								# reading from memory
								# dont think we need this...
								# if type(d[1][1]) is int:
								# 	self.register[d[0][1]] = self.memory[d[1][1]:d[1][1]+3]
								# el
								if d[1][1] == "sp":
									# this only happens in return instructions.
									self.register["iar"] = \
										self.memory[self.register["sp"]:self.register["sp"]+3]
							else:
								self.register["iar"] = d[1]
				else:
					# branch wasnt taken but we predicted it was
					# print "flushed no branch"
					self.register["iar"] = ins.iar+8

				# print self.register["iar"]
				if ins.brto == self.register["iar"]:
					self.fetch.update_predictor(ins.iar, self.register["iar"], True)
				else:
					Unit.flush_all()
					ins.pred_br = False
					self.fetch.update_predictor(ins.iar, self.register["iar"], False)
					break
			else:
				if ins.lex in ["jmp", "br", "nbr", "call", "return"]:
					ins.pred_br = True
					self.fetch.update_predictor(ins.iar, ins.brto, True)

		self.buffer = []
		# self.register["iar"] += 4

	def shift(self):
		for ins in self.buffer:
			# self.register.rename(ins, True)
			self.obus.appendleft(ins)
		self.buffer = []

	def io_getc(self):
		if len(self.io_in) > 0:
			c, self.io_in = self.io_in[0], self.io_in[1:]
			return c
		return -1

	def io_read(self, target):
		tokens = self.io_in.split()
		val = None
		tok = ""

		if self._reg(target) < 64:
			for t in tokens:
				try:
					val = int(t)
					tok = t
					break
				except ValueError:
					pass
		elif self._reg(target) >= 64:
			for t in tokens:
				try:
					val = float(t)
					tok = t
					break
				except ValueError:
					pass

		if val != None:
			self.io_in = self.io_in[self.io_in.index(tok)+len(tok):]
		return val

	# links to the fetch stage to update local branch prediction
	def link_fetch(self, ft):
		self.fetch = ft

	def flush(self):
		self.buffer = []
		self.register.flush()

#*		Log
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
# keeps a log of all the instructions executed as well as some other statistics
class Log(Unit):
	def __init__(self, sim, upre=None):
		super(Log, self).__init__(sim, upre)
		self.sim = sim
		self.ins = []
		self.changes = []
		self.cycles = 0
		self.halt = False
		self.settings = sim.settings

	def clk(self):
		self.cycles += 1
		while True:
			try:
				ins = self.ibus.pop()

				if self.settings["log"]:
					self.ins.append(( ins, self.cycles ))

				if ins.lex == "print":
					if len(ins.op) > 0:
						print [self._val(p) for p in ins.op]
					# else:
					# 	print self.register

				if ins.lex == "halt":
					self.halt = True

			except IndexError:
				break

	def shift(self):
		pass

	def __str__(self):
		if self.settings["log"]:
			self.ins = [i for i in self.ins if i[0].lex != "halt"]
			norm_cycles = self.ins[-1][1] - self.ins[0][1] +1 if len(self.ins) > 0 else 1
			brpred_results = [i.pred_br for i,c in self.ins if hasattr(i, "pred_br")]
			
			if len(brpred_results) == 0:
				brpred_results = [True]

			strrep = "Execution Log:\n"
			# strrep += "               IPC: "+str(len(self.ins)/float(self.cycles)) \
			# 	+ " ins/cycle ("+str(len(self.ins)) \
			# 	+ " instructions total; "+str(self.cycles)+" cycles total)\n"
			strrep += "                   IPC: " \
				+ str(len(self.ins)/float(norm_cycles)) \
				+ " ins/cycle ("+str(len(self.ins))+" instructions total; " \
				+ str(norm_cycles)+" cycles total)\n"
			strrep += "  Branch misprediction: "+str(brpred_results.count(False)*100/float(len(brpred_results)))+"%\n"

			if self.settings["ins-log"]:
				strrep += "  Instructions log:\n\n"
				strrep += "  cycle |   id  |   iar  |          assembler        -> effect\n"
				strrep += "--------+-------+--------+----------------------------------------------------\n"
				for ins, cycle in self.ins:
					strrep += "  "+("{0:>6}").format(cycle)+str(ins)+"\n"
		else:
			strrep = "Log unit was disabled."

		return strrep+"\n"