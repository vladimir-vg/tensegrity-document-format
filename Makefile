# you can specify explicit path to matlab executable
# to be used in tests
MATLAB_EXEC_PATH = /mnt/external-hdd-seagate-ultra-slim/matlab_installation/bin/matlab

deps:
	pip3 install -r requirements.txt

test: generate_tdfs_from_examples
	PYTHONPATH=`pwd` MATLAB_EXEC_PATH=$(MATLAB_EXEC_PATH) pytest tests

generate_tdfs_from_examples: \
	tests/generated_data/SixBar_plain.tdf \
	tests/generated_data/SixBar_diamond.tdf \
	tests/generated_data/SixBar_diamond_classless.tdf \
	tests/generated_data/SixBar_pentagon.tdf \
	tests/generated_data/SixBar_pentagon_classless.tdf

tests/generated_data/%.tdf: examples/%.tdf.xacro
	# $@ is target value, $< is source file
	xacro $< > $@

.PHONY: deps test generate_tdfs_from_examples


# write command here, just not to lose it
# TODO: turn it into makefile command, specify path to NTRT as constant
#
# PYTHONPATH=`pwd` python3 ./py_tdf/tdf2ntrt_yaml.py tests/generated_data/SixBar_diamond.tdf  > SixBar_diamond.yaml
# ../NTRTsim/build/yamlbuilder/BuildModel ./SixBar_diamond.yaml
