function convert_MATtoNC(path_src, path_out, date)
    A = load(path_src);
    fn = fieldnames(A);
    [nlat, nlon] = size(A.Xp);

    ncid = netcdf.create(path_out,'NC_WRITE');
    dimlat  = netcdf.defDim(ncid,'lat',nlat);
    dimlon  = netcdf.defDim(ncid,'lon',nlon);
    dimtime = netcdf.defDim(ncid,'time',length(date));
    idlon   = netcdf.defVar(ncid,'lon','NC_DOUBLE',dimlon);
    idlat   = netcdf.defVar(ncid,'lat','NC_DOUBLE',dimlat);
    idtime  = netcdf.defVar(ncid,'time','NC_DOUBLE',dimtime);
    for k=3:numel(fn)
        var    = fn{k};
        id = netcdf.defVar(ncid,var,'NC_DOUBLE',[dimlon dimlat]);
    end
    netcdf.endDef(ncid);
    for k=3:numel(fn)
        var    = fn{k};
        data   = transpose(A.(var));
        netcdf.putVar(ncid,k,data);
    end
    netcdf.putVar(ncid, idlon, A.Xp(1,:))
    netcdf.putVar(ncid, idlat, A.Yp(:,1))
    netcdf.putVar(ncid, idtime, date)
    netcdf.close(ncid);
end
% ncid2 = netcdf.open('somefile.nc','NC_NOWRITE');
% data_copy = netcdf.getVar(ncid2,0);
% if isequal(longitude,data_copy)
%       disp('Data match');
% else
%       disp('Data mis-match');
% end

