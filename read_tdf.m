% This function accepts path to *.tdf file
%
% If your tensegrity file has *.tdf.xarco extension
% you need to do macro expansion via 'xarco file.tdf.xarco > file.tdf' first
function Res = read_tdf(filepath)
  root = xml2struct(filepath);

  %% algorithm:
  %% 1) walk the <rod>, <cable>, <node>
  %%    entries, collect all mentioned node ids.
  %% 2) Sort them by name. Index of the id in sorted array
  %%    would index in resulting matrices
  %% 3) read mapping class-name -> rest_length, stiffness
  %% 4) Walk <rod> and <cable> entries again, filling C and R matrices.
  %%    Also match class by name as set rest_length and stiffness_coef values
  %% 5) Read nodes positions

  % empty string array
  node_ids = string.empty

  for i = 1:length(root.tdf.composition.rod)
    node_ids = add_unique(node_ids, root.tdf.composition.rod{i}.Attributes.node1)
    node_ids = add_unique(node_ids, root.tdf.composition.rod{i}.Attributes.node2)
  end
  for i = 1:length(root.tdf.composition.cable)
    node_ids = add_unique(node_ids, root.tdf.composition.cable{i}.Attributes.node1)
    node_ids = add_unique(node_ids, root.tdf.composition.cable{i}.Attributes.node2)
  end
  sorted_ids = sort(node_ids)

  rod_class = collect_attributes(root.tdf.rod_class)
  cable_class = collect_attributes(root.tdf.cable_class)

  %% We collected all ids of nodes and stiffness/rest_length params
  %% Now we need to walk <cable> and <rod> and populate resulting matrices

  n = length(sorted_ids)
  Res.Cables = zeros(n, n)
  Res.Rods = zeros(n, n)
  Res.rest_lengths = zeros(n, n)
  Res.stiffness_coefs = zeros(n, n)

  for k = 1:length(root.tdf.composition.rod)
    i = find(sorted_ids == root.tdf.composition.rod{k}.Attributes.node1)
    j = find(sorted_ids == root.tdf.composition.rod{k}.Attributes.node2)

    class_name = root.tdf.composition.rod{k}.Attributes.class
    stiffness = rod_class.(class_name).stiffness
    rest_length = rod_class.(class_name).rest_length

    Res.Cables(i,j) = 1
    Res.Cables(j,i) = 1
    Res.stiffness_coefs(i,j) = stiffness
    Res.stiffness_coefs(j,i) = stiffness
    Res.rest_lengths(i,j) = rest_length
    Res.rest_lengths(j,i) = rest_length
  end

  for k = 1:length(root.tdf.composition.cable)
    i = find(sorted_ids == root.tdf.composition.cable{k}.Attributes.node1)
    j = find(sorted_ids == root.tdf.composition.cable{k}.Attributes.node2)

    class_name = root.tdf.composition.cable{k}.Attributes.class
    stiffness = cable_class.(class_name).stiffness
    rest_length = cable_class.(class_name).rest_length

    Res.Rods(i,j) = 1
    Res.Rods(j,i) = 1
    Res.stiffness_coefs(i,j) = stiffness
    Res.stiffness_coefs(j,i) = stiffness
    Res.rest_lengths(i,j) = rest_length
    Res.rest_lengths(j,i) = rest_length
  end

  function result = collect_attributes(elements)
    result = struct
    if isstruct(elements)
      id = elements.Attributes.id
      result.(id) = struct
      result.(id).stiffness = str2num(elements.Attributes.stiffness)
      result.(id).rest_length = str2num(elements.Attributes.rest_length)
    else
      for i = 1:length(elements)
        id = elements{i}.Attributes.id
        result.(id) = struct
        result.(id).stiffness = str2num(elements{i}.Attributes.stiffness)
        result.(id).rest_length = str2num(elements{i}.Attributes.rest_length)
      end
    end
  end

  function result = add_unique(list, element)
    if any(list(:) == element)
      result = list
    else
      list(end+1) = element
      result = list
    end
  end
end
