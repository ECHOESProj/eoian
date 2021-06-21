
## https://cran.r-project.org/web/packages/ecmwfr/vignettes/cds_vignette.html
## https://rpubs.com/markpayne/358146
## http://chris35wills.github.io/netcdf-R/

install.packages("ecmwfr")
install.packages("keyring")
install.packages("metR") 
install.packages("udunits2") 

library(ecmwfr)
library(keyring)

library(metR)
library(ggplot2)
library(data.table)
library(raster)

## ECMWF connection to Online account
wf_set_key(service = "webapi")

##Declaring of  variables
ERAI_monthly <- wf_archetype(
  request = list(
    class   = "ei",
    dataset = "interim",
    date    = "19790101/19790201/19790301/19790401/19790501/19790601/19790701/19790801/19790901/19791001/19791101/19791201",
    expver  = "1",
    grid    = "0.75/0.75",
    levtype = "sfc",
    param   = "167.128",
    stream  = "moda",
    type    = "an",
    target  = "output",
    format  = "netcdf"),
  dynamic_fields = c("date", "grid", "target"))

# Retriving of dates.
format_dates <- function(dates) {
  dates <- as.Date(dates)
  paste0(lubridate::year(dates),
         formatC(lubridate::month(dates), width = 2, flag = "0"),
         formatC(lubridate::day(dates), width = 2, flag = "0"),
         collapse = "/")
}

# Formatting of dates
format_dates(c("2018-01-01", "2018-02-01"))

dates <- seq.Date(as.Date("1988-08-01"), as.Date("2018-08-01"), "1 year")

# Building of data
my_request <- ERAI_monthly(date = format_dates(dates), 
                           grid = "3/3",
                           target = "august_monthly.nc")
str(my_request)

# Requesting of data
wf_request(request = my_request,
           user = "ckelly@compass.ie", 
           transfer = TRUE,
           path = "D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST", 
           verbose = FALSE)



august_temp <- ReadNetCDF("D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\august_monthly.nc")

world <- list(geom_path(data = map_data("world2"), 
                        aes(long, lat, group = group), 
                        size = 0.2, color = "gray50"),
              coord_quickmap(),
              scale_x_longitude(),
              scale_y_latitude())


ggplot(august_temp[time == time[1]], aes(longitude, latitude)) +
  geom_contour_fill(aes(z = t2m - 273.15)) +
  world +
  scale_fill_divergent("2m temperature (°C)") +
  metR:::theme_field()

trends <- august_temp[, FitLm(year = year(time), t2m, se = TRUE), 
                      by = .(longitude, latitude)] 
trends[, p.value :=  pt(abs(estimate)/std.error, df, lower.tail = FALSE)]

ggplot(trends[term == "year"], aes(longitude, latitude)) +
  geom_contour_fill(aes(z = estimate*10), 
                    breaks = AnchorBreaks(0, 0.25, exclude = 0)) +
  stat_subset(aes(subset = p.value <= 0.01), 
              geom = "point", size = 0.1, alpha = 0.5) +
  world +
  scale_fill_divergent("2m temperature \ntrend (°C/decade)") +
  metR:::theme_field() +
  labs(subtitle = "August mean temperature change 1988-2018", 
       caption = "Data: ERA Interim")


# Reading of Climate Change Service data
wf_set_key(service = "cds")

#UID 57431
#API Key5df3d699-1f06-4141-a210-81959898dab0

# NETCDF Request of parameters

request <- list("dataset_short_name" = "reanalysis-era5-pressure-levels",
                "product_type"   = "reanalysis",
                "variable"       = "temperature",
                "pressure_level" = "850",
                "year"           = "2000",
                "month"          = "04",
                "day"            = "04",
                "time"           = "00:00",
                "area"           = "70/-20/30/60",
                "format"         = "netcdf",
                "target"         = "era5-demo.nc")

# Request from database
ncfile <- wf_request(user = "57431",
                     request = request,   
                     transfer = TRUE,  
                     path = "~",
                     verbose = FALSE)

# Conversion of NetCDF to Raster
r <- raster::raster(ncfile)

# Plotting of data
raster::plot(r, main = "ERA-5 Reanalysis Demo (2m Temperature 850 hPa)")
maps::map("world", add = TRUE)

# Subsetting of ECHOES area
ROI <- extent(-8,-2,50,55)

# Crop data to ECHOES area
r.crop <- crop(r,ROI)

# Plot subsetted area
plot(r.crop)
maps::map("world", add = TRUE)

# Write subsetted data to file
writeRaster(r.crop,"D:\\Projects\\Active\\Intereg_Echeos\\RF_TEST\\TEST.tif",format="GTiff", overwrite=TRUE)



## Grib Request of parameters
request <- list("dataset_short_name" = "seasonal-original-single-levels",
                'originating_centre'= 'ukmo',
                'system'= '14',
                'variable'= '2m_temperature',
                'year'= '2019',
                'month'= '10',
                "day"= "01",
                'leadtime_hour'=  '6',
                'format'= 'grib')

# Request from database
ncfile <- wf_request(user = "57431",
                     request = request,   
                     transfer = TRUE,  
                     path = "~",
                     verbose = FALSE)

## zip file
request <- list("dataset_short_name" = "projections-cordex-single-levels",
                'experiment'= 'evaluation',
                'variable'= 'mean_precipitation_flux',
                'gcm_model'= 'era_interim',
                'rcm_model'= 'cclm4_8_17',
                'ensemble_member'= 'r1i1p1',
                'format'= 'zip',
                "temporal_resolution"= "daily_mean",
                'simulation_version'=  'v1',
                'start_year'=  '2006',
                'end_year'=  '2008'
                )

ncfile1 <- wf_request(user = "57431",
                     request = request,   
                     transfer = TRUE,  
                     path = "~",
                     verbose = FALSE)
