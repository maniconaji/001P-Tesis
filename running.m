clear all
clc
path = dir(fullfile('Output/mat_block/','*.mat'));
for i=1:length(path)    
    names = split(path(i).name,"-")
    path_name = string(names(2))+'0000'
    dt = str2num(['uint64(',replace(path_name,"T",""),')']);
    disp(path(i).name)
    disp(dt)
    path_src=strcat('Output/mat_block/',path(i).name);
    path_out=strcat('Output/nc_block/',replace(path(i).name,".mat",".nc"));
    convert_MATtoNC(path_src, path_out, dt)
end
