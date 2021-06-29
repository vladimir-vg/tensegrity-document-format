import xml.etree.ElementTree as ElementTree

def extract_classes_with_indexes(prefix, connectivity, stiffness_coef, rest_lengths):
    # key is a tuple with stiffness and rest_length
    # value: list of indexes that have this class
    classes = {}
    for i in range(len(connectivity)):
        for j in range(len(connectivity[i])):
            if connectivity[i][j] != 0:
                key = (stiffness_coef[i][j], rest_lengths[i][j])
                if not key in classes:
                    classes[key] = []
                # matrix is symmetric
                # we sort indexes, so this way we won't have
                # same pairs of indexes
                pair0 = [i,j]
                pair0.sort()
                pair = tuple(pair0)
                if not pair in classes[key]:
                    classes[key].append(pair)

    # Okay, we collected properties and indexes
    # now we need to turn it into convenient form
    result = []
    for (i, ((stiffness, rest_length), pairs)) in enumerate(classes.items()):
        result.append({
            'id': f'{prefix}{i}',
            'stiffness': str(stiffness),
            'rest_length': str(rest_length),
            'pairs': pairs,
        })
    return result



def to_xml(data):
    root = ElementTree.Element('tdf')

    rod_classes = None
    cable_classes = None

    are_classes_used = ('stiffness_coef' in data) and ('rest_lengths' in data)
    if are_classes_used:
        rod_classes = extract_classes_with_indexes('rod', data['Rods'], data['stiffness_coef'], data['rest_lengths'])
        cable_classes = extract_classes_with_indexes('cable', data['Cables'], data['stiffness_coef'], data['rest_lengths'])

        for c in rod_classes:
            ElementTree.SubElement(root, 'rod_class',
                id=c['id'], stiffness=c['stiffness'], rest_length=c['rest_length'])
        for c in cable_classes:
            ElementTree.SubElement(root, 'cable_class',
                id=c['id'], stiffness=c['stiffness'], rest_length=c['rest_length'])

    n = len(data['Rods'])

    index_name_mapping = None
    if 'node_ids' in data:
        index_name_mapping = dict(enumerate(data['node_ids']))
    else:
        index_name_mapping = dict([(i, f'node{i}') for i in range(n)])

    composition = ElementTree.SubElement(root, 'composition')
    saved_index_pairs = set()
    for i in range(n):
        for j in range(n):
            pair0 = [i,j]
            pair0.sort()
            pair = tuple(pair0)
            if pair in saved_index_pairs:
                continue

            attrs = {'node1': index_name_mapping[i], 'node2': index_name_mapping[j]}
            if data['Rods'][i][j] != 0:
                if are_classes_used:
                    [class_item, *rest] = filter(lambda x: pair in x['pairs'], rod_classes)
                    attrs['class'] = class_item['id']
                ElementTree.SubElement(composition, 'rod', attrs)
                saved_index_pairs.add(pair)

            if data['Cables'][i][j] != 0:
                if are_classes_used:
                    [class_item, *rest] = filter(lambda x: pair in x['pairs'], cable_classes)
                    attrs['class'] = class_item['id']
                ElementTree.SubElement(composition, 'cable', attrs)
                saved_index_pairs.add(pair)

    initial_positions = ElementTree.SubElement(root, 'initial_positions')
    for i in range(len(data['nodes_position'][0])):
        id = index_name_mapping[i]
        x = data['nodes_position'][0][i]
        y = data['nodes_position'][1][i]
        z = data['nodes_position'][2][i]
        xyz = f'{x} {y} {z}'
        ElementTree.SubElement(initial_positions, 'node', id=id, xyz=xyz)

    return ElementTree.tostring(root)
