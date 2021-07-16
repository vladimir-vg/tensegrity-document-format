function xmltext = to_tdf_xml(robot)
  docNode = com.mathworks.xml.XMLUtils.createDocument('tdf');

  n = length(robot.Rods);

  node_ids = string.empty;
  if isfield(robot, 'node_ids')
    node_ids = robot.node_ids;
  else
    for i = 1:n
      % use indexing starting from zero in names
      % to match same behavior in Python code
      node_ids(i) =  'node' + string(i-1);
    end
  end

  [rod_classes, cable_classes, class_elements_to_create] = read_classes_and_prepare_elements(robot);
  append_elements(docNode, docNode.getDocumentElement, class_elements_to_create);

  cable_rod_elements_to_create = prepare_rod_cable_elements(robot, node_ids, rod_classes, cable_classes);
  composition = docNode.createElement('composition');
  append_elements(docNode, composition, cable_rod_elements_to_create);
  docNode.getDocumentElement.appendChild(composition);

  position_elements = prepare_position_elements(robot, node_ids);
  initial_positions = docNode.createElement('initial_positions');
  append_elements(docNode, initial_positions, position_elements);
  docNode.getDocumentElement.appendChild(initial_positions);

  xmltext = xmlwrite(docNode);

  function append_elements(docNode, parent, elements_to_create)
    for i = 1:length(elements_to_create)
      name = elements_to_create(i).name;
      attrs = elements_to_create(i).attrs;
      node = docNode.createElement(name);
      keys = fieldnames(attrs);
      for j = 1:length(keys)
        node.setAttribute(keys{j,1}, attrs.(keys{j,1}));
      end
      parent.appendChild(node);
    end
  end

  function position_elements = prepare_position_elements(robot, node_ids)
    position_elements = struct('name',{},'attrs',{});

    n = size(robot.Rods, 1);
    for i = 1:n
      x = robot.nodes_position(1, i);
      y = robot.nodes_position(2, i);
      z = robot.nodes_position(3, i);
      xyz = string(x) + ' ' + string(y) + ' ' + string(z);
      attrs = struct('id', node_ids(i), 'xyz', xyz);
      position_elements(end+1) = struct('name', 'node', 'attrs', attrs);
    end
  end

  function cable_rod_elements_to_create = prepare_rod_cable_elements(robot, node_ids, rod_classes, cable_classes)
    cable_rod_elements_to_create = struct('name',{},'attrs',{});

    are_classes_used = (length(rod_classes) ~= 0);
    n = size(robot.Rods, 1);
    saved_index_pairs = [];

    for i = 1:n
      for j = 1:n
        pair = [i, j];
        if i > j
          pair = [j, i];
        end

        if isempty(saved_index_pairs) || ~isempty(ismember(saved_index_pairs, pair, 'rows'))
          attrs = struct('node1', node_ids(i), 'node2', node_ids(j));

          if robot.Rods(i,j) ~= 0
            if are_classes_used
              for k = 1:size(rod_classes, 1)
                if find(ismember(rod_classes(k).pairs, pair, 'rows'))
                  attrs.class = rod_classes(k).id;
                end
              end
            end

            cable_rod_elements_to_create(end+1) = struct('name', 'rod', 'attrs', attrs);
            saved_index_pairs(end+1, :) = pair;
          end

          if robot.Cables(i,j) ~= 0
            if are_classes_used
              for k = 1:size(cable_classes, 1)
                if find(ismember(cable_classes(k).pairs, pair, 'rows'))
                  attrs.class = cable_classes(k).id;
                end
              end
            end

            cable_rod_elements_to_create(end+1) = struct('name', 'cable', 'attrs', attrs);
            saved_index_pairs(end+1, :) = pair;
          end

        end
      end
    end
  end

  function [rod_classes, cable_classes, class_elements_to_create] = read_classes_and_prepare_elements(robot)
    rod_classes = [];
    cable_classes = [];
    class_elements_to_create = struct('name',{},'attrs',{});

    %%%
    are_classes_used = isfield(robot, 'stiffness_coef');
    if are_classes_used
      rod_classes = extract_classes_with_indexes('rod', robot.Rods, robot.stiffness_coef, robot.rest_lengths);
      cable_classes = extract_classes_with_indexes('cable', robot.Cables, robot.stiffness_coef, robot.rest_lengths);
    end

    for i = 1:length(rod_classes)
      attrs = struct('id', rod_classes(i).id, 'stiffness', rod_classes(i).stiffness, 'rest_length', rod_classes(i).rest_length);
      class_elements_to_create(end+1) = struct('name', 'rod_class', 'attrs', attrs);
    end
    for i = 1:length(cable_classes)
      attrs = struct('id', cable_classes(i).id, 'stiffness', cable_classes(i).stiffness, 'rest_length', cable_classes(i).rest_length);
      class_elements_to_create(end+1) = struct('name', 'cable_class', 'attrs', attrs);
    end
  end

  function result = extract_classes_with_indexes(prefix, connectivity, stiffness_coef, rest_lengths)
    props = [];
    pairs = struct; % idx => list

    n = size(connectivity, 1);

    for i = 1:n
      for j = 1:n
        if connectivity(i, j) ~= 0
          key = [stiffness_coef(i,j), rest_lengths(i,j)];
          idx = [];
          if ~isempty(props)
            idx = find(ismember(props, key, 'rows'));
          end

          if isempty(idx)
            props(end+1, :) = key;
            idx = size(props, 1); % numbers of rows
            pairs.(prefix+string(idx)) = [];
          end
          idxkey = prefix + string(idx);

          pair = [i, j];
          if i > j
            pair = [j, i];
          end

          if isempty(pairs.(idxkey))
            pairs.(idxkey) = pair;
          else
            if isempty(find(ismember(pairs.(idxkey), pair, 'rows')))
              pairs_arr = pairs.(idxkey);
              pairs_arr(end+1, :) = pair;
              pairs.(idxkey) = pairs_arr;
            end
          end
        end
      end
    end

    result = struct('id',{},'pairs',{},'stiffness',{},'rest_length',{});
    for i = 1:size(props, 1)
      cl = struct;
      stiffness = props(i, 1);
      rest_length = props(i, 2);
      cl.id = prefix + string(i);
      cl.pairs = pairs.(cl.id);
      cl.stiffness = string(stiffness);
      cl.rest_length = string(rest_length);
      result(end+1) = cl;
    end
  end


end
