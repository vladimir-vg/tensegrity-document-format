function tdf_read_write_read(path)
  %% add root directory to load path, so function read_tdf could be loaded
  userpath(strcat(pwd, '/../matlab_src'));

  robot1 = read_tdf(path);
  xmltext = to_tdf_xml(robot1);
  robot2 = read_tdf(xmltext);
  txt = jsonencode(robot2);
  disp(txt);
  exit;
end
