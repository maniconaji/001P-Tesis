
import numpy as np
import math

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def get_values_from_nodos(i, df, nodos, variables):
    # variables = [altura, periodo, dirección]
    x1, y1, x2, y2 = nodos[i]
    subdf = df.loc[(df['longitude']==x1)&(df["latitude"]==y1)]
    hs, tp, dp = subdf[variables].values[0]
    return x1, y1, x2, y2, hs, tp, dp

def model_parameters(key, **kwargs):
    area = kwargs["area"]
    def extract_parameters_from_area(area, resolution_grid, **kwargs):
        N, W, S, E = area
        xpc, ypc = W, S
        xlenc, ylenc = (E-W), (N-S)
        mxc, myc = round_up(xlenc*(3600/resolution_grid)), round_up(ylenc*(3600/resolution_grid))
        return xpc, ypc, xlenc, ylenc, mxc, myc

    xpc, ypc, xlenc, ylenc, mxc, myc = extract_parameters_from_area(area, kwargs["resolution_grid"])
    if key == "grid":    
        flow, fhigh = kwargs["frequency"]
        msc = round_up(np.log10(fhigh/flow)/np.log10(1+0.1))
        return xpc, ypc, kwargs["alpc"], xlenc, ylenc, mxc, myc, kwargs["mdc"], flow, fhigh, msc
    elif key == "bathymetry":
        xpinp, ypinp, alpinp, mxinp, myinp, arc_seconds = kwargs["bathymetry"]
        dxyinp = arc_seconds*(1/3600)
        return xpinp, ypinp, alpinp, mxinp, myinp, dxyinp, dxyinp
    elif key == "names_bath":
        fac, name, idla, nhedf = kwargs["names_bath"]
        return fac, name, idla, nhedf
    elif key == "numeric":
        dabs, drel, curvat, npnts, mxitst, alfa = kwargs["numeric"]
        return dabs, drel, curvat, npnts, mxitst, alfa
    elif key == "subgrid":
        xpn, ypn, xlen, ylen, mxn, myn = extract_parameters_from_area(kwargs["subarea"], kwargs["resolution_subgrid"])
        return xpn, ypn, kwargs["alpn"], xlen, ylen, mxn, myn
    elif key == "group":
        ix1, ix2, iy1, iy2 = 0, mxc, 0, myc
        return ix1, ix2, iy1, iy2
    elif key == "ray":
        xp1, yp1, xq1, yq1, nint, xp, yp, xq, yq = xpc, ypc, (xpc + xlenc), ypc, (myc + 1), xpc, (ypc + ylenc), (xpc + xlenc), (ypc + ylenc)
        return xp1, yp1, xq1, yq1, nint, xp, yp, xq, yq
    elif key == "output":
        ndec, len = 9, mxc
    return ndec, len

def EscrituraSwanFile(df, path_out, model, nodos, parameters, variables, **kwargs):
    for n, time in enumerate(df.time):
        subdf = df[df['time']==time]
        fecha = time.strftime("%Y%m%dT%H")
        name_file = path_out+"/"+fecha+"_"+model+".swn"
        file = open(name_file, "w")
        file.write(
        f'$******************************  HEADING  *************************************\n'
        f'PROJ \'Memoria\' \'M\' \n'
        f'$ OBTENCION ESPECTROS ANIDACION PARA MODELO: {model}, HORA: {time} \n'
        f'$**************************   MODEL STARTUP  **********************************\n'
        f'SET NAUTical\nCOORDinates SPHErical CCM\n'
        f'$****************************  MODEL INPUT  ***********************************\n'
        f'CGRID REGular %.2f %.2f %.2f %.2f %.2f %i %i CIRCLE %i %.2f %.2f %i' %(model_parameters("grid", **kwargs)) +'\n'
        f'INPgrid BOTtom REGular %.5f %.5f %.2f %d %d %.7f %.7f' %(model_parameters("bathymetry", **kwargs)) +'\n'
        f'READinp BOTtom %.1f \'%s\' %i %i FREE' %(model_parameters("names_bath", **kwargs)) +'\n'
        f'$*****************    INPUT BOUNDARY SPECTRAL CONDITIONS   ********************\n'
        )
        if ("P1" in model):
            for nodo_key in nodos.keys():
                file.write(
                    f'BOUNdspec SEGMent XY %.2f %.2f %.2f %.2f CONstant PAR %.2f %.2f %.2f' %(get_values_from_nodos(nodo_key, subdf, nodos, variables)) +'\n'
                    )
        elif ("P2" in model) or ("P3" in model):
            file.write(
                    f'BOUNdnest1 NEst \'Output/dat/{fecha}_{model}.dat\' \n'
                )
        file.write(
            f'$****************************     PHYSICS    **********************************\n'
            f'BREAking CONSTANT 1.0 0.42\n'
            f'OFF QUADRUPL\nOFF WCAPPING\n'
            f'$***************************      NUMERICS   **********************************\n'
            f'NUM STOPC dabs=%.3f drel=%.3f curvat=%.3f npnts=%.3f STAT mxitst=%i alfa=%.3f' %(model_parameters("numeric", **kwargs)) +'\n'
            f'$***************************** OUTPUT REQUESTS  *******************************\n'
            )
        if len(kwargs["sub_area"])==0:
            pass
        else:
            for nsub, sub in enumerate(kwargs["sub_area"]):
                if ("P1" in model):
                    submodel = "P2"
                elif ("P2" in model):
                    submodel = "P3"
                file.write(
                    f'NGRid \'{submodel}-{nsub+1}\' %.2f %.2f %.2f %.2f %.2f %i %i '%(model_parameters("subgrid", subarea=sub, **kwargs)) +'\n'
                    f'NESTout \'{submodel}-{nsub+1}\' \'Output/dat/{fecha}_P2-{nsub+1}.dat\' \n'
                    f'$\n'
                    )
        file.write(
            f'GROUP \'OUTPUT\' SUBGRID %i %i %i %i' %(model_parameters("group", **kwargs)) +'\n'
            f'OUTPut OPTIons BLOCK %i %i' %(model_parameters("output", **kwargs)) +'\n'
            f'BLOCK \'OUTPUT\' NOHEADER \'Output/block-mat/{fecha}_{model}.mat\' LAY-OUT 1 '+parameters+' \n'
            f'$\n'
            f'POINts \'Points\' FILE \'Points.pnt\' \n'
            f'TABLe \'Points\' NOHEADER \'Output/point/{fecha}_{model}.txt\' '+parameters+' \n'
            f'$\n'
            f'RAY \'RAY\' %.2f %.2f %.2f %.2f %i %.2f %.2f %.2f %.2f' %(model_parameters("ray", **kwargs)) +'\n'
            f'$\n'
            )
        for depth in np.arange(50, 200 + 50, 50):
            name_veril = "V0%i" %(depth) if (depth < 100) else "V%i" %(depth)
            file.write(
                f'ISOline \'%s\' \'RAY\' DEPth %i' %(name_veril, depth) +'\n'
                f'TABLe \'%s\' NOHEADER \'Output/isoline/{fecha}_{model}_%s.txt\' '%(name_veril, name_veril) +parameters+' \n'
                f'$\n'
            )
        file.write(
            f'$\n'
            f'TEST 1,0\n'
            f'COMPUTE\n'
            f'STOP')
        file.close()
    return