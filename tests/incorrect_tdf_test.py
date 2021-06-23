import pytest

import py_tdf

# Things to check:
# - для пары i-j было объявлено два разных соединения
# - для пары i-j было объявлено одно соединение разных классов
# - для узла использованного в описании не указана начальная позиция
# - начальная позиция указана больше одного раза, и с разными значениями
# - длины rest_length не соответствуют указанным позициям

def test_minimal_correct_tdf():
    # shouldn't raise any error
    py_tdf.from_string('''
<?xml version="1.0"?>
<tdf>
    <rod_class id="rod1" stiffness="100" rest_length="0.5" />
    <cable_class id="cable1" stiffness="10" rest_length="0.25" />
    <composition>
        <rod class="rod1" node1="A" node2="B" />
        <rod class="rod1" node1="C" node2="D" />
        <cable class="cable1" node1="A" node2="C" />
        <cable class="cable1" node1="B" node2="D" />
    </composition>
    <initial_positions>
        <node id="A" xyz="1 1 0" />
        <node id="B" xyz="1 -1 0" />
        <node id="C" xyz="-1 1 0" />
        <node id="D" xyz="-1 -1 0" />
    </initial_positions>
</tdf>
'''.strip())

def test_rod_class_is_absent():
    with pytest.raises(py_tdf.TDFValidationError):
        py_tdf.from_string('''
<?xml version="1.0"?>
<tdf>
    <cable_class id="cable1" stiffness="10" rest_length="0.25" />
    <composition>
        <rod class="rod1" node1="A" node2="B" />
        <rod class="rod1" node1="C" node2="D" />
        <cable class="cable1" node1="A" node2="C" />
        <cable class="cable1" node1="B" node2="D" />
    </composition>
    <initial_positions>
        <node id="A" xyz="1 1 0" />
        <node id="B" xyz="1 -1 0" />
        <node id="C" xyz="-1 1 0" />
        <node id="D" xyz="-1 -1 0" />
    </initial_positions>
</tdf>
'''.strip())

def test_rod_class_not_specified():
    with pytest.raises(py_tdf.TDFValidationError):
        py_tdf.from_string('''
<?xml version="1.0"?>
<tdf>
    <rod_class id="rod1" stiffness="100" rest_length="0.5" />
    <cable_class id="cable1" stiffness="10" rest_length="0.25" />
    <composition>
        <rod node1="A" node2="B" />
        <rod node1="C" node2="D" />
        <cable class="cable1" node1="A" node2="C" />
        <cable class="cable1" node1="B" node2="D" />
    </composition>
    <initial_positions>
        <node id="A" xyz="1 1 0" />
        <node id="B" xyz="1 -1 0" />
        <node id="C" xyz="-1 1 0" />
        <node id="D" xyz="-1 -1 0" />
    </initial_positions>
</tdf>
'''.strip())

def test_rod_class_with_such_name_not_present():
    with pytest.raises(py_tdf.TDFValidationError):
        py_tdf.from_string('''
<?xml version="1.0"?>
<tdf>
    <rod_class id="rod1" stiffness="100" rest_length="0.5" />
    <cable_class id="cable1" stiffness="10" rest_length="0.25" />
    <composition>
        <rod class="not-rod1" node1="A" node2="B" />
        <rod class="not-rod1" node1="C" node2="D" />
        <cable class="cable1" node1="A" node2="C" />
        <cable class="cable1" node1="B" node2="D" />
    </composition>
    <initial_positions>
        <node id="A" xyz="1 1 0" />
        <node id="B" xyz="1 -1 0" />
        <node id="C" xyz="-1 1 0" />
        <node id="D" xyz="-1 -1 0" />
    </initial_positions>
</tdf>
'''.strip())

# TODO: add exactly same tests for cable class
