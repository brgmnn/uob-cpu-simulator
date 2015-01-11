#!/bin/sh
time ./simulator.py hex/image/gaussian-blur.hex -in=puppy.pgm -out=batch/puppy-1.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-1.pgm -out=batch/puppy-2.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-2.pgm -out=batch/puppy-3.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-3.pgm -out=batch/puppy-4.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-4.pgm -out=batch/puppy-5.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-5.pgm -out=batch/puppy-6.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-6.pgm -out=batch/puppy-7.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-7.pgm -out=batch/puppy-8.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-8.pgm -out=batch/puppy-9.pgm
time ./simulator.py hex/image/gaussian-blur.hex -in=batch/puppy-9.pgm -out=batch/puppy-10.pgm
