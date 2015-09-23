begin
           hrrrFile = getenv("hrrrFile") ; HRRR data
           gfsFile = getenv("rapFile") ; RAP data
           outFile = getenv("outFile") ; outFile data
           indexFlag = getenv("INDEX")
           
           if(indexFlag .eq. "true") then
              indexf = addfile("index.nc","r") 
              index = indexf->index
           end if
     
           f1 = addfile(hrrrFile,"r") 
           f2 = addfile(gfsFile,"r") 
           system("rm -f "+outFile)

           fout = addfile(outFile,"c")

           dd = dimsizes(f1->T2D)
            print("dd="+dd)
           dimlat = dd(0)
           dimlon = dd(1)



           v1d = ndtooned(f1->T2D)
           if(indexFlag .eq. "false") then
               findexOut = addfile("index_out.nc","c")
               index = ind(ismissing(v1d) )
               findexOut->index = index
               system("mv index_out.nc index.nc")
               exit 
           end if
           v1dgfs = ndtooned(f2->T2D)
           v1d(index) = v1dgfs(index)
           T2D = onedtond(v1d,(/dimlat,dimlon/))
           fout->T2D = T2D

; Downward long wave radiation using GFS.
           v1d = ndtooned(f2->LWDOWN)
           LWDOWN = onedtond(v1d,(/dimlat,dimlon/))
           fout->LWDOWN = LWDOWN

           v1d = ndtooned(f1->Q2D)
           v1dgfs = ndtooned(f2->Q2D)
           v1d(index) = v1dgfs(index)
           Q2D = onedtond(v1d,(/dimlat,dimlon/))
           fout->Q2D = Q2D

           v1d = ndtooned(f1->U2D)
           v1dgfs = ndtooned(f2->U2D)
           v1d(index) = v1dgfs(index)
           U2D = onedtond(v1d,(/dimlat,dimlon/))
           fout->U2D = U2D

           v1d = ndtooned(f1->V2D)
           v1dgfs = ndtooned(f2->V2D)
           v1d(index) = v1dgfs(index)
           V2D = onedtond(v1d,(/dimlat,dimlon/))
           fout->V2D = V2D

           v1d = ndtooned(f1->PSFC)
           v1dgfs = ndtooned(f2->PSFC)
           v1d(index) = v1dgfs(index)
           PSFC = onedtond(v1d,(/dimlat,dimlon/))
           fout->PSFC = PSFC

           v1d = ndtooned(f1->RAINRATE)
           v1dgfs = ndtooned(f2->RAINRATE)
           v1d(index) = v1dgfs(index)
           RAINRATE = onedtond(v1d,(/dimlat,dimlon/))
           fout->RAINRATE = RAINRATE

           v1d = ndtooned(f1->SWDOWN)
           v1dgfs = ndtooned(f2->SWDOWN)
           v1d(index) = v1dgfs(index)
           SWDOWN = onedtond(v1d,(/dimlat,dimlon/))
           fout->SWDOWN = SWDOWN

;           v1d = ndtooned(f1->WEASD)
;           v1dgfs = ndtooned(f2->WEASD)
;           v1d(index) = v1dgfs(index)
;           WEASD = onedtond(v1d,(/dimlat,dimlon/))
;           fout->WEASD = WEASD
           

end
