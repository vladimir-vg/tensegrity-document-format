# you can specify explicit path to matlab executable
# to be used in tests
MATLAB_EXEC_PATH = matlab

deps:
	pip3 install -r requirements.txt

test: generate_tdfs_from_examples
	PYTHONPATH=`pwd` MATLAB_EXEC_PATH=$(MATLAB_EXEC_PATH) pytest

generate_tdfs_from_examples: \
	tests/generated_data/SixBar_plain.tdf \
	tests/generated_data/SixBar_diamond.tdf \
	tests/generated_data/SixBar_pentagon.tdf

# TODO: find a way to write same without repetitions
tests/generated_data/SixBar_plain.tdf: examples/SixBar_plain.tdf.xacro
	xacro examples/SixBar_plain.tdf.xacro > tests/generated_data/SixBar_plain.tdf
tests/generated_data/SixBar_diamond.tdf: examples/SixBar_diamond.tdf.xacro
	xacro examples/SixBar_diamond.tdf.xacro > tests/generated_data/SixBar_diamond.tdf
tests/generated_data/SixBar_pentagon.tdf: examples/SixBar_pentagon.tdf.xacro
	xacro examples/SixBar_pentagon.tdf.xacro > tests/generated_data/SixBar_pentagon.tdf

.PHONY: deps test generate_tdfs_from_examples
