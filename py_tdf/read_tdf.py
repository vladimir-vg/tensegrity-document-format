import xml.etree.ElementTree as ElementTree
import numpy as np

from py_tdf.validate import validate

def from_path(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    validate(root)
    return read_tdf(root)

def from_string(content):
    root = ElementTree.fromstring(content)
    validate(root)
    return read_tdf(root)

def has_at_least_one_classless_element(rods, cables):
    rod_classes = {}
    cable_classes = {}

    # populate
    for el in rods:
        ids = [el.attrib['node1'], el.attrib['node2']]
        ids.sort()
        id = " -- ".join(ids)
        if not 'class' in el.attrib:
            if not id in rod_classes:
                rod_classes[id] = None
        else:
            if not id in rod_classes:
                rod_classes[id] = el.attrib['class']
            else:
                if rod_classes[id] != el.attrib['class']:
                    raise f'Two different classes "{rod_classes[id]}" and "{el.attrib["class"]}" were used for element: "{id}"'
    for el in cables:
        ids = [el.attrib['node1'], el.attrib['node2']]
        ids.sort()
        id = " -- ".join(ids)
        if not 'class' in el.attrib:
            if not id in cable_classes:
                cable_classes[id] = None
        else:
            if not id in cable_classes:
                cable_classes[id] = el.attrib['class']
            else:
                if cable_classes[id] != el.attrib['class']:
                    raise f'Two different classes "{cable_classes[id]}" and "{el.attrib["class"]}" were used for element: "{id}"'

    def has_no_class(pair):
        (id, class_name) = pair
        return (class_name is None)

    has_rod_without_a_class = any(map(has_no_class, rod_classes.items()))
    has_cable_without_a_class = any(map(has_no_class, cable_classes.items()))
    return (has_rod_without_a_class or has_cable_without_a_class)

# for now just return dictionary similar to interface in matlab
# probably it might be more convenient to add some kind of OO interface.
# We'll see
#
# If at least one rod or cable doesn't have class specified,
# then stiffness & rest matrices are not returned. Only C, R matrices
def read_tdf(root):
    rods = root.findall('composition')[0].findall('rod')
    cables = root.findall('composition')[0].findall('cable')

    ids_set = set()
    for el in rods:
        ids_set.add(el.attrib['node1'])
        ids_set.add(el.attrib['node2'])
    for el in cables:
        ids_set.add(el.attrib['node1'])
        ids_set.add(el.attrib['node2'])
    node_ids = sorted(list(ids_set))
    n = len(node_ids)

    rod_class = collect_attributes(root.findall('rod_class'))
    cable_class = collect_attributes(root.findall('cable_class'))

    # if at least one element doesn't have class, then we can't compute
    # proper stiffness and rest_length matrices
    # Thus, do not return them, only C and R matrices
    should_collect_prop_matrices = not has_at_least_one_classless_element(rods, cables)

    r, r_stiffness, r_rest_lengths = populate_matrices(n, node_ids, rod_class, rods, should_collect_prop_matrices)
    c, c_stiffness, c_rest_lengths = populate_matrices(n, node_ids, cable_class, cables, should_collect_prop_matrices)

    robot = {}
    robot['Cables'] = c
    robot['Rods'] = r
    robot['Connectivity'] = r + c
    robot['node_ids'] = node_ids
    robot['nodes_position'] = np.zeros((3, n))

    if should_collect_prop_matrices:
        robot['stiffness_coef'] = r_stiffness + c_stiffness
        robot['rest_lengths'] = r_rest_lengths + c_rest_lengths

    positions = root.findall('initial_positions')[0].findall('node')
    for pos in positions:
        idx = node_ids.index(pos.attrib['id'])
        [x, y, z] = map(float, pos.attrib['xyz'].split())
        robot['nodes_position'][0][idx] = x
        robot['nodes_position'][1][idx] = y
        robot['nodes_position'][2][idx] = z

    return robot

def collect_attributes(class_elements):
    result = {}
    for el in class_elements:
        result[el.attrib['id']] = {
            'stiffness': float(el.attrib['stiffness']),
            'rest_length': float(el.attrib['rest_length']),
        }
    return result

def populate_matrices(n, node_ids, el_class, elements, should_collect_prop_matrices):
    m = np.zeros((n, n))
    m_stiffness = np.zeros((n, n))
    m_rest_lengths = np.zeros((n, n))
    for el in elements:
        i = node_ids.index(el.attrib['node1'])
        j = node_ids.index(el.attrib['node2'])

        m[i][j] = 1
        m[j][i] = 1

        if should_collect_prop_matrices:
            class_name = el.attrib['class']
            stiffness = el_class[class_name]['stiffness']
            rest_length = el_class[class_name]['rest_length']
            m_stiffness[i][j] = stiffness
            m_stiffness[j][i] = stiffness
            m_rest_lengths[i][j] = rest_length
            m_rest_lengths[j][i] = rest_length

    return m, m_stiffness, m_rest_lengths
