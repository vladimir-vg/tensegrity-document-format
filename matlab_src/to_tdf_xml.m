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

  function [rod_classes, cable_classes, class_elements_to_create] = read_classes_and_prepare_elements(robot)
    rod_classes = struct;
    cable_classes = struct;
    class_elements_to_create = [struct('name', 'rod_class', 'attrs', struct('node1', 'val1'))];

    %%%
  end
end
