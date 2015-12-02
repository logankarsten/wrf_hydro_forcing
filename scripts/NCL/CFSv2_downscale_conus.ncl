;-----------------------------------------------------------------------------------------
;    CFSv2_downscale_conus.ncl
;
;
;    Project: WRF-Hydro IOC for National Water Center
;
;    Authors: Logan Karsten
;             National Center for Atmospheric Research
;             Research Applications Laboratory
;             karsten@ucar.edu
;             303-497-2693
;
;    Purpose: This is a top-level NCL script that will
;             downscale regridded CFSv2 bias-corrected
;             data to the conus IOC WRF-Hydro domain.
;
;    Usage: ncl 'hgtFileSrc="/d4/karsten/IOC/param/CFSv2_hght.nc"'
;               'hgtFileDst="/d4/karsten/IOC/param/geo_dst.nc"'
;               'inFile="/d4/karsten/IOC/tmp/CFSv2_bias_corrected_TMP_
;                       2015020100_2015021413_regridded.M02.nc"'
;               'outFile="/d4/karsten/IOC/WRF_Hydro_input/2015020100/
;                         2015021413.LDASIN_DOMAIN2"'
;               'lapseFile="/d4/karsten/IOC/param/lapse_rate.nc"'
;               'verYYYYMMDDHH="2015021413"'
;
;------------------------------------------------------------------------------------------

external TOPO_ADJF90 "/d4/karsten/DFE/IOC_TESTING/long_range/programs/topo_adjf90.so"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRF_contributed.ncl"

begin

  ;------------------------
  ; Open input files
  ;------------------------

  f1 = addfile(inFile,"r")
  f2 = addfile(hgtFileSrc,"r")
  f3 = addfile(hgtFileDst,"r")  
  f4 = addfile(lapseFile,"r") ; NARR lapse rate

  ;-----------------
  ; Input variables
  ;-----------------

  lapse = f4->lapse
  HGT_src = f2->HGT
  HGT_dst = f3->HGT_M(0,:,:)
  T2D_in = f1->T2D
  Q2D_in = f1->Q2D
  PSFC_in = f1->PSFC

  ;----------------------------------------------------
  ; These variables aren't downscaled, but still
  ; need to be read in as they will be in the final
  ; output file.
  ;----------------------------------------------------

  U2D_in = f1->U2D
  V2D_in = f1->V2D
  LWDOWN_in = f1->LWDOWN
  RAINRATE_in = f1->RAINRATE
  lon_in=f1->XLONG_M
  lat_in=f1->XLAT_M
  dims=dimsizes(lat_in)
  nlat = dims(0)
  nlon = dims(1)

  ;----------------------------------------------------
  ; Variables needed for shortwave downscaling
  ;----------------------------------------------------

  ; No need to re-read destination elevation grid
  swdown_in_double = f1->SWDOWN
  xlat = f3->XLAT_M(0,:,:)
  xlong = f3->XLONG_M(0,:,:)
  dx = f3@DX
  dy = f3@DY
  nsizes = dimsizes(HGT_dst)
  nx = nsizes(1)
  ny = nsizes(0)
  cosa = f3->COSALPHA(0,:,:)
  sina = f3->SINALPHA(0,:,:)
  swdown_out_double = swdown_in_double*0.
  yyyy = toint(str_get_cols(verYYYYMMDDHH,0,3))
  mon = toint(str_get_cols(verYYYYMMDDHH,4,5))
  dd = toint(str_get_cols(verYYYYMMDDHH,6,7))
  hh = toint(str_get_cols(verYYYYMMDDHH,8,9))
  xtime_int = hh*60 
  yyyy@calendar = "julian"
  julian_int = day_of_year(yyyy,mon,dd)
  xtime = tofloat(xtime_int)
  julian = tofloat(julian_int)

  swdown_in = tofloat(swdown_in_double)
  swdown_out = tofloat(swdown_out_double)
  
  TOPO_ADJF90:: topo_adj(HGT_dst,xlat,xlong,dx,dy,nx,ny,cosa,sina,xtime, \
                julian,swdown_in,swdown_out)
  
  ;----------------------------------------------------
  ; These variables aren't downscaled, but still
  ; need to be read in as they will be in the final
  ; output file.
  ;----------------------------------------------------

  U2D_in = f1->U2D
  V2D_in = f1->V2D
  LWDOWN_in = f1->LWDOWN
  SWDOWN_in = f1->SWDOWN
  RAINRATE_in = f1->RAINRATE
  lat_in=f1->XLAT_M
  lon_in=f1->XLONG_M
  dims=dimsizes(lat_in)
  nlat = dims(0)
  nlon = dims(1)

  ;---------------------------------
  ; Perform downscaling
  ;---------------------------------

  W2D = Q2D_in/(1-Q2D_in)
  RH = relhum(T2D_in,W2D,PSFC_in)
  RH = RH < 100
  DHGT = HGT_src-HGT_dst
  T2D_out = T2D_in+DHGT*lapse/1000.
  PSFC_out = PSFC_in+DHGT*PSFC_in/287.05/T2D_out*9.8
  Q2D_out = mixhum_ptrh(PSFC_out/100., T2D_out, RH, 2)

  ; Current data is 2D, need to add third time dimension for
  ; final output
  T2D_final = new((/1,nlat,nlon/),"double")
  Q2D_final = new((/1,nlat,nlon/),"double")
  U2D_final = new((/1,nlat,nlon/),"double")
  V2D_final = new((/1,nlat,nlon/),"double")
  PSFC_final = new((/1,nlat,nlon/),"double")
  RAINRATE_final = new((/1,nlat,nlon/),"double")
  LWDOWN_final = new((/1,nlat,nlon/),"double")
  SWDOWN_final = new((/1,nlat,nlon/),"double")

  ; Flip data to write south to north
  ;T2D_out = T2D_out(::-1,:)
  ;Q2D_out = Q2D_out(::-1,:)
  ;U2D_in = U2D_in(::-1,:)
  ;V2D_in = V2D_in(::-1,:)
  ;PSFC_out = PSFC_out(::-1,:)
  ;RAINRATE_in = RAINRATE_in(::-1,:)
  ;LWDOWN_in = LWDOWN_in(::-1,:)
  ;SWDOWN_in = SWDOWN_in(::-1,:)

  T2D_final(0,:,:) = T2D_out(:,:)
  Q2D_final(0,:,:) = Q2D_out(:,:)
  U2D_final(0,:,:) = U2D_in(:,:)
  V2D_final(0,:,:) = V2D_in(:,:)
  PSFC_final(0,:,:) = PSFC_out(:,:)
  RAINRATE_final(0,:,:) = RAINRATE_in(:,:)
  LWDOWN_final(0,:,:) = LWDOWN_in(:,:)
  SWDOWN_final(0,:,:) = swdown_out(:,:) 
  
  ;--------------------------------
  ; Establish meta-data
  ;--------------------------------

  lat_in@FieldType = 104
  lat_in@MemoryOrder = 104
  lat_in@units = "degrees latitude"
  lat_in@description = "Latitude on mass grid"
  lat_in@stagger = "M"
  lat_in@sr_x = 1
  lat_in@sr_y = 1

  lon_in@FieldType = 104
  lon_in@MemoryOrder = 104
  lon_in@units = "degrees longitude"
  lon_in@description = "Longitude on mass grid"
  lon_in@stagger = "M"
  lon_in@sr_x = 1
  lon_in@sr_y = 1

  T2D_final@missing_value = 1.e+20
  T2D_final@_FillValue = 1.e+20
  T2D_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  T2D_final@units = "K"
  T2D_final@long_name = "2-m Air Temperature"

  Q2D_final@missing_value = 1.e+20
  Q2D_final@_FillValue = 1.e+20
  Q2D_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  Q2D_final@units = "kg/kg"
  Q2D_final@long_name = "2-m specific humidity"

  U2D_final@missing_value = 1.e+20
  U2D_final@_FillValue = 1.e+20
  U2D_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  U2D_final@units = "m/s"
  U2D_final@long_name = "10-m U-wind component"

  V2D_final@missing_value = 1.e+20
  V2D_final@_FillValue = 1.e+20
  V2D_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  V2D_final@units = "m/s"
  V2D_final@long_name = "10-m V-wind component"

  PSFC_final@missing_value = 1.e+20
  PSFC_final@_FillValue = 1.e+20
  PSFC_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  PSFC_final@units = "Pa"
  PSFC_final@long_name = "Surface Pressure"

  RAINRATE_final@missing_value = 1.e+20
  RAINRATE_final@_FillValue = 1.e+20
  RAINRATE_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  RAINRATE_final@units = "mm s^-1"
  RAINRATE_final@long_name = "RAINRATE"
  RAINRATE_final@description = "RAINRATE"

  LWDOWN_final@missing_value = 1.e+20
  LWDOWN_final@_FillValue = 1.e+20
  LWDOWN_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear"
  LWDOWN_final@units = "W/m^2"
  LWDOWN_final@long_name = "Surface downward longwave radiation"

  SWDOWN_final@missing_value = 1.e+20
  SWDOWN_final@_FillValue = 1.e+20
  SWDOWN_final@remap = "remapped via ESMF_regrid_with_weights: Bilinear" 
  SWDOWN_final@units = "W/m^2"
  SWDOWN_final@long_name = "Surface downward shortwave radiation"

  ;-------------------------------- 
  ; Output to final LDASIN files
  ;--------------------------------

  ; Open NetCDF file for writing
  ncdf = addfile(outFile,"c")

  ; Define global attributes
  fAtt = True
  fAtt@title = "Fully downscaled CFSv2 data for long-range WRF-Hydro conus configuration"
  fAtt@creation_date = systemfunc("date")
  fAtt@author = "National Center for Atmospheric Research"
  fAtt@Conventions = "None"
  fileattdef(ncdf,fAtt)

  ; Define coordinate variables and their dimensionality
  dimNames = (/"Time","south_north","west_east"/)
  dimNames2 = (/"south_north","west_east"/)
  dimSizes = (/-1,nlat,nlon/)
  dimUnlim = (/True,False,False/)
  filedimdef(ncdf,dimNames,dimSizes,dimUnlim)

  ; Predefine the dimensionality of the variables to be written out
  filevardef(ncdf,"lat",typeof(lat_in),dimNames2)
  filevarattdef(ncdf,"lat",lat_in)
  ncdf->lat = (/lat_in/)

  filevardef(ncdf,"lon",typeof(lon_in),dimNames2)
  filevarattdef(ncdf,"lon",lon_in)
  ncdf->lon = (/lon_in/)

  filevardef(ncdf,"XLAT_M",typeof(lat_in),dimNames2)
  filevarattdef(ncdf,"XLAT_M",lat_in)
  ncdf->XLAT_M = (/lat_in/)
   
  filevardef(ncdf,"XLONG_M",typeof(lon_in),dimNames2)
  filevarattdef(ncdf,"XLONG_M",lon_in)
  ncdf->XLONG_M = (/lon_in/)

  filevardef(ncdf,"T2D",typeof(T2D_final),dimNames)
  filevarattdef(ncdf,"T2D",T2D_final)
  ncdf->T2D = (/T2D_final/) 
 
  filevardef(ncdf,"Q2D",typeof(Q2D_final),dimNames)
  filevarattdef(ncdf,"Q2D",Q2D_final)
  ncdf->Q2D = (/Q2D_final/)

  filevardef(ncdf,"U2D",typeof(U2D_final),dimNames)
  filevarattdef(ncdf,"U2D",U2D_final)
  ncdf->U2D = (/U2D_final/)

  filevardef(ncdf,"V2D",typeof(V2D_final),dimNames)
  filevarattdef(ncdf,"V2D",V2D_final)
  ncdf->V2D = (/V2D_final/)

  filevardef(ncdf,"PSFC",typeof(PSFC_final),dimNames)
  filevarattdef(ncdf,"PSFC",PSFC_final)
  ncdf->PSFC = (/PSFC_final/)

  filevardef(ncdf,"RAINRATE",typeof(RAINRATE_final),dimNames)
  filevarattdef(ncdf,"RAINRATE",RAINRATE_final)
  ncdf->RAINRATE = (/RAINRATE_final/)

  filevardef(ncdf,"LWDOWN",typeof(LWDOWN_final),dimNames)
  filevarattdef(ncdf,"LWDOWN",LWDOWN_final)
  ncdf->LWDOWN = (/LWDOWN_final/)

  filevardef(ncdf,"SWDOWN",typeof(SWDOWN_final),dimNames)
  filevarattdef(ncdf,"SWDOWN",SWDOWN_final)
  ncdf->SWDOWN = (/SWDOWN_final/)

end 
