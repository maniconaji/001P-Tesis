clear all
clc
path = dir(fullfile('Output/block-mat/','*.mat'));
for i=1:length(path)    
%     dt = datetime(replace(path(i).name,"_P1.mat",""),'InputFormat', 'yyyyMMdd''T''HH', 'TimeZone','UTC');
    dt = str2num(['uint64(',replace(replace(path(i).name,"_P1.mat","0000"),"T",""),')']);
    disp(path(i).name)
%     disp(replace(path(i).name,".mat",".nc"))
    disp(dt)
    path_src=strcat('Output/block-mat/',path(i).name);
    path_out=strcat('Output/block-nc/',replace(path(i).name,".mat",".nc"));
    convert_MATtoNC(path_src, path_out, dt)
end
