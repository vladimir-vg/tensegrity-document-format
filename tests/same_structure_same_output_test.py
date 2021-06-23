import os
import json
import deepdiff
import itertools
import pytest

import py_tdf

# TODO: matlab starts really slow. Instead of reading single file on each matlab run
# we could rewrite tdf_to_json_dump.m to read several files at once

# We need to test that for several files output matrices are same.
# Also need to check that it is the same for both python and matlab reader

MATLAB_EXEC_PATH = os.environ['MATLAB_EXEC_PATH']

# All files in same list should produce same output,
# since they describe same structure
FILES_DESCRIBING_SAME_STURCTURE = [
    ['SixBar_diamond.tdf', 'SixBar_pentagon.tdf', 'SixBar_plain.tdf'],
]



def expand_path(filename):
    return os.path.abspath(f'tests/generated_data/{filename}')

def matlab_read(path):
    # matlab prints some useless information on every run, even when ran without GUI.
    # We want to get json output from tdf_to_json_dump function.
    # In order to workaround this, we just add '| tail -n 2' to the command.
    # This way we read only last line of the output, which is going to be json output.
    # This hack works only if json output doesn't contain any newline characters,
    # which is always true when json is displayed without pretty printing
    matlab_cmd = f'{MATLAB_EXEC_PATH} -nodisplay -nosplash -nodesktop -r "tdf_to_json_dump(\'{path}\');"'
    # we need to run this command from the 'tests' directory
    # tdf_to_json_dump.m script expects that
    cmd = f'cd tests && {matlab_cmd} | tail -n 2'
    print(cmd)
    with os.popen(cmd) as f:
        output = f.read()
        # matlab outputs command line prompt right after output that we interested in
        # just take json output, ignore the rest
        json_text = output.strip().split("\n")[0]
        return json.loads(json_text)

def python_read(path):
    robot = py_tdf.from_path(path)
    # python tdf reader returns numpy arrays
    # need to convert them to lists, so it would be compared as plain json
    return {
        'Cables': robot['Cables'].tolist(),
        'Rods': robot['Rods'].tolist(),
        'Connectivity': robot['Connectivity'].tolist(),
        'stiffness_coef': robot['stiffness_coef'].tolist(),
        'rest_lengths': robot['rest_lengths'].tolist(),
        'nodes_position': robot['nodes_position'].tolist(),
        'node_ids': robot['node_ids'],
    }



@pytest.fixture(params=FILES_DESCRIBING_SAME_STURCTURE)
def input_paths(request):
    paths = request.param
    return list(map(lambda filename: (filename, expand_path(filename)), paths))

# we need to check that all outputs for files are same
# this fixture produces pairs of values to compare
@pytest.fixture
def all_json_dump_pair_combinations(input_paths):
    # TODO: add outputs from python version of reader to comparison
    output_values1 = [(filename, 'matlab', matlab_read(path)) for (filename, path) in input_paths]
    # output_values1 = []
    output_values2 = [(filename, 'python', python_read(path)) for (filename, path) in input_paths]
    pairs = itertools.combinations(output_values1 + output_values2, 2)
    return pairs



def test_different_files_have_same_output(all_json_dump_pair_combinations):
    for (item1, item2) in all_json_dump_pair_combinations:
        (filename1, _, value1) = item1
        (filename2, _, value2) = item2
        diff = deepdiff.DeepDiff(value1, value2, ignore_numeric_type_changes=True)
        assert (len(diff) == 0), f'{filename1} and {filename2} have different output\n{diff.pretty()}'
