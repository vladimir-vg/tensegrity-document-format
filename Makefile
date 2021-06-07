deps:
	pip3 install -r requirements.txt

test: generate_tdfs_from_examples

generate_tdfs_from_examples: \
	tests/SixBar_plain.tdf \
	tests/SixBar_diamond.tdf \
	tests/SixBar_pentagon.tdf

# TODO: find a way to write same without repetitions
tests/SixBar_plain.tdf: examples/SixBar_plain.tdf.xacro
	xacro examples/SixBar_plain.tdf.xacro > tests/SixBar_plain.tdf
tests/SixBar_diamond.tdf: examples/SixBar_diamond.tdf.xacro
	xacro examples/SixBar_diamond.tdf.xacro > tests/SixBar_diamond.tdf
tests/SixBar_pentagon.tdf: examples/SixBar_pentagon.tdf.xacro
	xacro examples/SixBar_pentagon.tdf.xacro > tests/SixBar_pentagon.tdf

.PHONY: deps test generate_tdfs_from_examples
