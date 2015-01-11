#!/bin/sh
./simulator.py hex/instruction-test/mov.hex --generate-test-data
./simulator.py hex/instruction-test/add.hex --generate-test-data
./simulator.py hex/instruction-test/br.hex --generate-test-data
./simulator.py hex/instruction-test/div.hex --generate-test-data
./simulator.py hex/instruction-test/halt.hex --generate-test-data
./simulator.py hex/instruction-test/jmp.hex --generate-test-data
./simulator.py hex/instruction-test/load.hex --generate-test-data
./simulator.py hex/instruction-test/mov.hex --generate-test-data
./simulator.py hex/instruction-test/mul.hex --generate-test-data
./simulator.py hex/instruction-test/nbr.hex --generate-test-data
./simulator.py hex/instruction-test/negative.hex --generate-test-data
./simulator.py hex/instruction-test/nop.hex --generate-test-data
./simulator.py hex/instruction-test/store.hex --generate-test-data
./simulator.py hex/instruction-test/sub.hex --generate-test-data
