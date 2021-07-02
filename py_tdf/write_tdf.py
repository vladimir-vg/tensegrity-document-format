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



def read_classes_and_prepare_elements(data):
    rod_classes = None
    cable_classes = None
    elements_to_create = []

    are_classes_used = ('stiffness_coef' in data) and ('rest_lengths' in data)
    if are_classes_used:
        rod_classes = extract_classes_with_indexes('rod', data['Rods'], data['stiffness_coef'], data['rest_lengths'])
        cable_classes = extract_classes_with_indexes('cable', data['Cables'], data['stiffness_coef'], data['rest_lengths'])

        for c in rod_classes:
            elements_to_create.append(('rod_class', {
                'id': c['id'], 'stiffness': c['stiffness'], 'rest_length': c['rest_length']
            }))
        for c in cable_classes:
            elements_to_create.append(('cable_class', {
                'id': c['id'], 'stiffness': c['stiffness'], 'rest_length': c['rest_length']
            }))

    return rod_classes, cable_classes, elements_to_create



def prepare_rod_cable_elements(data, index_name_mapping, rod_classes, cable_classes):
    elements_to_create = []

    are_classes_used = (rod_classes != None)
    n = len(data['Rods'])
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
                elements_to_create.append(('rod', attrs))
                saved_index_pairs.add(pair)

            if data['Cables'][i][j] != 0:
                if are_classes_used:
                    [class_item, *rest] = filter(lambda x: pair in x['pairs'], cable_classes)
                    attrs['class'] = class_item['id']
                elements_to_create.append(('cable', attrs))
                saved_index_pairs.add(pair)

    return elements_to_create



def prepare_position_elements(data, index_name_mapping):
    elements_to_create = []

    n = len(data['Rods'])
    for i in range(n):
        id = index_name_mapping[i]
        x = data['nodes_position'][0][i]
        y = data['nodes_position'][1][i]
        z = data['nodes_position'][2][i]
        xyz = f'{x} {y} {z}'
        elements_to_create.append(('node', {'id': id, 'xyz': xyz}))

    return elements_to_create



def to_xml(data):
    root = ElementTree.Element('tdf')

    n = len(data['Rods'])

    index_name_mapping = None
    if 'node_ids' in data:
        index_name_mapping = dict(enumerate(data['node_ids']))
    else:
        index_name_mapping = dict([(i, f'node{i}') for i in range(n)])

    rod_classes, cable_classes, class_elements_to_create = read_classes_and_prepare_elements(data)
    for (name, attrs) in class_elements_to_create:
        ElementTree.SubElement(root, name, attrs)

    composition = ElementTree.SubElement(root, 'composition')
    cable_rod_elements_to_create = prepare_rod_cable_elements(data, index_name_mapping, rod_classes, cable_classes)
    for (name, attrs) in cable_rod_elements_to_create:
        ElementTree.SubElement(composition, name, attrs)

    position_elements = prepare_position_elements(data, index_name_mapping)
    initial_positions = ElementTree.SubElement(root, 'initial_positions')
    for (name, attrs) in position_elements:
        ElementTree.SubElement(initial_positions, name, attrs)

    return ElementTree.tostring(root)
