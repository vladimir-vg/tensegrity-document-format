import xml.etree.ElementTree as ElementTree
import numpy as np

# for now just return dictionary similar to interface in matlab
# probably it might be more convenient to add some kind of OO interface
# we'll see
def read_tdf(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()

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

    r, r_stiffness, r_rest_lengths = populate_matrices(n, rod_class, rods)
    c, c_stiffness, c_rest_lengths = populate_matrices(n, cable_class, cables)

    robot = {}
    robot['Cables'] = c
    robot['Rods'] = r
    robot['Connectivity'] = r + c
    robot['stiffness_coef'] = r_stiffness + c_stiffness
    robot['rest_lengths'] = r_rest_lengths + c_rest_lengths
    robot['node_ids'] = node_ids
    robot['nodes_position'] = np.zeros((3, n))

    positions = root.findall('initial_positions')[0].findall('node')
    for pos in positions:
        idx = nodes_ids.index(pos.attrib['id'])
        [x, y, z] = map(float, pos.attrib['xyz'].split())
        robot['nodes_position'][0, idx] = x
        robot['nodes_position'][1, idx] = x
        robot['nodes_position'][2, idx] = x

    return robot

def collect_attributes(class_elements):
    result = {}
    for el in class_elements:
        result[el.attrib['id']] = {
            'stiffness': float(el.attrib['stiffness']),
            'rest_length': float(el.attrib['rest_length']),
        }
    return result

def populate_matrices(n, el_class, elements):
    m = np.zeros((n, n))
    m_stiffness = np.zeros((n, n))
    m_rest_lengths = np.zeros((n, n))
    for el in elements:
        i = node_ids.index(el.attrib['node1'])
        j = node_ids.index(el.attrib['node2'])
        class_name = el.attrib['class']
        stiffness = el_class[class_name]['stiffness']
        rest_length = el_class[class_name]['rest_length']

        m[i][j] = 1
        m[j][i] = 1
        m_stiffness[i][j] = stiffness
        m_stiffness[j][i] = stiffness
        m_rest_lengths[i][j] = rest_length
        m_rest_lengths[j][i] = rest_length
    return m, m_stiffness, m_rest_lengths
