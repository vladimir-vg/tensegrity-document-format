#/usr/bin/env python3
import sys
import yaml
import xml.etree.ElementTree as ElementTree

from py_tdf.validate import validate

# NTRT yaml expects node ids to be alphanumeric
# plain numbers are not allowed
ID_PREFIX = 'a_'



def tdf2ntrt_yaml(tdf_path):
    tree = ElementTree.parse(tdf_path)
    root = tree.getroot()

    validate(tree)

    # just map it to JSON-like structure, no additional checks
    # assuming that tdf is correct
    result = {'nodes': {}, 'pair_groups': {}, 'builders': {}}
    positions = root.findall('initial_positions')[0].findall('node')

    for pos in positions:
        id = f"{ID_PREFIX}{pos.attrib['id']}"
        [x, y, z] = list(map(float, pos.attrib['xyz'].split()))
        result['nodes'][id] = [x+10, y+10, z+10]

    rods = root.findall('composition')[0].findall('rod')
    for el in rods:
        id1 = f"{ID_PREFIX}{el.attrib['node1']}"
        id2 = f"{ID_PREFIX}{el.attrib['node2']}"
        class_name = f"{ID_PREFIX}{el.attrib['class']}"
        result['pair_groups'][class_name] = result['pair_groups'].get(class_name, [])
        result['pair_groups'][class_name].append([id1, id2])

    cables = root.findall('composition')[0].findall('cable')
    for el in cables:
        id1 = f"{ID_PREFIX}{el.attrib['node1']}"
        id2 = f"{ID_PREFIX}{el.attrib['node2']}"
        class_name = f"{ID_PREFIX}{el.attrib['class']}"
        result['pair_groups'][class_name] = result['pair_groups'].get(class_name, [])
        result['pair_groups'][class_name].append([id1, id2])

    for el in root.findall('rod_class'):
        id = f"{ID_PREFIX}{el.attrib['id']}"
        result['builders'][id] = {
            'class': 'tgRodInfo',
            'parameters': {
                # 'stiffness': float(el.attrib['stiffness']),
                # as far as I understand, you do not specify rest_length
                # for rod in NTRT. Didn't find such config parameter.
                # I assume it is computed from node positions
                'density': 0.688,
                'radius': 0.05,
            }
        }
    for el in root.findall('cable_class'):
        id = f"{ID_PREFIX}{el.attrib['id']}"
        result['builders'][id] = {
            'class': 'tgBasicActuatorInfo',
            'parameters': {
                'stiffness': float(el.attrib['stiffness']),
                # 'damping': 10,
                # 'pretension': 1000,
                # 'minRestLength': float(el.attrib['stiffness']),
            }
        }

    return result

if __name__ == '__main__':
    # ran as a script, we need to split out YAML data for given tdf file
    [tdf_path, *rest] = sys.argv[1:]
    # print('path: ', tdf_path)
    values = tdf2ntrt_yaml(tdf_path)
    print(yaml.dump(values, default_flow_style=False))
