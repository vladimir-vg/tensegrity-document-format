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

  % rod_class = struct
  % for i = 1:length(root.tdf.rod_class)
  %   id = root.tdf.rod_class{i}.Attributes.id
  %   rod_class.(id) = struct
  %   rod_class.(id).stiffness = root.tdf.rod_class{i}.Attributes.stiffness
  %   rod_class.(id).rest_length = root.tdf.rod_class{i}.Attributes.rest_length
  % end
  %
  % cable_class = struct
  % for i = 1:length(root.tdf.cable_class)
  %   id = root.tdf.cable_class{i}.Attributes.id
  %   cable_class.(id) = struct
  %   cable_class.(id).stiffness = root.tdf.cable_class{i}.Attributes.stiffness
  %   cable_class.(id).rest_length = root.tdf.cable_class{i}.Attributes.rest_length
  % end

  % Res.sorted_ids = sorted_ids
  % Res.rod_class = rod_class
  % Res.cable_class = cable_class

  %% We collected all ids of nodes and stiffness/rest_length params
  %% Now we need to walk <cable> and <rod> and populate resulting matrices

  function result = add_unique(list, element)
    if any(list(:) == element)
      result = list
    else
      list(end+1) = element
      result = list
    end
  end
end
