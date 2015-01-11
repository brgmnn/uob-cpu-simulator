cc   = ./assembler.py
bin  = ./simulator.py

src := $(shell find src/ -type f -name '*.asm')
obj := $(patsubst src/%.asm, hex/%.hex, $(src))

all: clear clean $(obj)

gentest: $(obj)
	$(bin) $(obj) --generate-test-data

clear:
	clear



# compile to object
$(obj): hex/%.hex : src/%.asm
	$(cc) $^ -o $@

# clean intermediate files
clean:
	rm -rf hex/*
