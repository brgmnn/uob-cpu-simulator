#!/usr/bin/env python
import assembler, unit, simulator, sys
import unittest

class Execution(unittest.TestCase):
	def test_obj_mov(self):
		sim = simulator.Simulator("hex/instruction-test/mov.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/mov.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/mov.mem").readlines()))
	
	def test_obj_add(self):
		sim = simulator.Simulator("hex/instruction-test/add.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/add.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/add.mem").readlines()))
	def test_obj_sub(self):
		sim = simulator.Simulator("hex/instruction-test/sub.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/sub.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/sub.mem").readlines()))
	def test_obj_mul(self):
		sim = simulator.Simulator("hex/instruction-test/mul.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/mul.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/mul.mem").readlines()))
	def test_obj_div(self):
		sim = simulator.Simulator("hex/instruction-test/div.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/div.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/div.mem").readlines()))

	def test_obj_load(self):
		sim = simulator.Simulator("hex/instruction-test/load.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/load.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/load.mem").readlines()))
	def test_obj_store(self):
		sim = simulator.Simulator("hex/instruction-test/store.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/store.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/store.mem").readlines()))

	def test_obj_jmp(self):
		sim = simulator.Simulator("hex/instruction-test/jmp.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/jmp.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/jmp.mem").readlines()))
	def test_obj_br(self):
		sim = simulator.Simulator("hex/instruction-test/br.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/br.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/br.mem").readlines()))
	def test_obj_nbr(self):
		sim = simulator.Simulator("hex/instruction-test/nbr.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/nbr.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/nbr.mem").readlines()))

	def test_obj_nop(self):
		sim = simulator.Simulator("hex/instruction-test/nop.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/nop.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/nop.mem").readlines()))
	def test_obj_halt(self):
		sim = simulator.Simulator("hex/instruction-test/halt.hex")
		sim.run()
		self.assertEqual(repr(sim.register), "\n".join(open("hex/instruction-test/halt.reg").readlines()))
		self.assertEqual(repr(sim.memory), "\n".join(open("hex/instruction-test/halt.mem").readlines()))

#*		Main
#*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*#
if __name__ == "__main__":
	sys.stdout = open("/dev/null", "w")
	unittest.main()
