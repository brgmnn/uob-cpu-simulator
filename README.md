# CPU Simulator #

![](image/puppy.jpg?raw=true "Puppy")

A full featured processor simulator, which also includes an assembler to
assemble assembly code for the simulator. The puppy image above shows a before
and after of a greyscale image that was blurred with three iterations of a
Gaussian blur program written in the assembly of, and then executed on, the
simulator (this took 70 minutes to run!).

### Running ###

Assemble `.asm` files with either `./assembler.py input.asm -o output.hex`
where `input.asm` and `output.hex` are your desired assembly and hex files.
Alternatively use `make` if they are in the `src` folder.

Run the simulator with `./simulator.py path/to/program.hex`

### Features ###

* 64-bit instructions.
* Pipelined (6 deep).
* SuperScalar (width can be adjusted at runtime).
* Reservation Stations (out of order execution, non-blocking issue of
    instructions).
* Multiple execution units.
    * Multi-cycle instructions keep execution units busy for a long time.
    * Different kinds of execution units for: Arithmetic, fetching, branching,
        floating point etc.  Re-order buffer.
* Register renaming.
* Dynamic branch prediction using either address caching or local branch
    history and states.
* Vector instruction unit.
* Floating point support (for single and vector instructions).
* Stack instructions (push, pop).
* Subroutine call instructions (call return, which make use of the stack).
* File IO instructions. Reading/writing integers, floats and ASCII characters
    from a file stream.
* Unified collection of registers, perform vector and single instructions on
    the same registers.

### Possible fun additions ###

Some things that would be fun to add:

* A memory hierarchy with different cache levels.
* Better file IO support, read or write from any file on the file system.
* User input.
