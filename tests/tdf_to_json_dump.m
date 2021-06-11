function tdf_to_json_dump(path)
  %% add root directory to load path, so function read_tdf could be loaded
  userpath(strcat(pwd, '/..'));

  robot = read_tdf(path);
  txt = jsonencode(robot);
  disp(txt);
  exit;
end
