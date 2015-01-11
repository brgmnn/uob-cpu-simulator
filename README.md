# CPU Simulator #

![](image/puppy.pgm?raw=true "Puppy")

A full featured processor simulator, which also includes an assembler to
assemble assembly code for the simulator.

### Running ###

Assemble `.asm` files with either `./assembler.py input.asm -o output.hex`
where `input.asm` and `output.hex` are your desired assembly and hex files.
Alternatively use `make` if they are in the `src` folder.

Run the simulator with `./simulator.py path/to/program.hex`
