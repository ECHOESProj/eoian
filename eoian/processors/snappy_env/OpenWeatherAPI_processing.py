"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

import os
import pandas as pd
import geopandas as gpd
import requests
import sqlite3
from shapely import wkt

spatialite_location = r"C:\Users\ckelly.COMPASSINFORMAT\tools\mod_spatialite-NG-win-amd64;"

os.environ["PATH"] = (
            spatialite_location
            + os.environ["PATH"]
        )
# Read in Geopackage layer
def site_reader(geopack):
    sites_gdf = gpd.read_file(geopack, layer='test_sites')
    
    return sites_gdf

# Get the Centroid of each site
def get_centroid(geopack):
    sites_gdf = site_reader(geopack)
    cent_id = sites_gdf['geometry'].centroid
    #print(cent_id)

    return cent_id

# If weather was required for a town/city
def by_city():
    city = input('Enter your city : ')
    
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=81f5a3465ec3abf5ce734c45ef519ef4&units=metric'.format(city)
    res = requests.get(url)
    data = res.json()
    show_data(data,weather_id)

# Retrieve the data for a set location -- Data is returned as an array
def by_location(cent_id, group):
    for j,i in enumerate(cent_id):
        #print(cent_id[j].x, cent_id[j].y)
        #print(j,i)
        url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=81f5a3465ec3abf5ce734c45ef519ef4&units=metric'.format(cent_id[j].x, cent_id[j].y)
        res = requests.get(url)
        data = res.json()
        weather_id = j
        
        a = show_data(data,weather_id)
        #print(a)
        group.append(a)

    return group

# Process the data into a list
def show_data(data,weather_id):
    temp = data['main']['temp']
    wind_speed = data['wind']['speed']
    latitude = data['coord']['lat']
    longitude = data['coord']['lon']
    description = data['weather'][0]['description']
    weather_id = weather_id+1
    a = weather_id,temp,wind_speed, latitude, longitude, description

    return a

# Export data
# Weather data is converted to a dataframe, geopackage is called back in, both are merged and exported to Spaitalite.
def site_info(db_filename,geopack,group):
    sites_gdf = site_reader(geopack)
    df2 = pd.DataFrame(data=group)
    df2.columns = ['objectid','temp','wind_speed', 'latitude', 'longitude', 'description']

    sites_gdf['geometry'] = sites_gdf.geometry.apply(lambda x: wkt.dumps(x))
    merged_inner = sites_gdf.merge(df2,left_on='objectid',right_on='objectid',how='left')

    
    with sqlite3.connect(db_filename)as conn:

        conn.row_factory = sqlite3.Row  # results can then be used liked dicts
        conn.enable_load_extension(True)
        # load spatialite extension
        conn.execute('SELECT load_extension("mod_spatialite")')
        curs = conn.cursor()

        merged_inner.to_sql('weather_status', conn, if_exists='replace', index=False)
        sql = "SELECT AddGeometryColumn('weather_status', 'geom', 4326, 'MULTIPOLYGON', 'XY')"
        sql1 = "UPDATE weather_status SET geom=GeomFromText(geometry, 4326) "
        
        curs.execute(sql)
        curs.execute(sql1)
        conn.commit()
        print("Data has been exported to SQLite database")
    
def main():
    
    geopack = "D:\Projects\Active\Intereg_Echeos\Echoes_Climate_Forcast.gpkg"
    
    db_filename = r"D:/Projects/Active/Intereg_Echeos/Echoes_processing_db.sqlite"
    
    group = []

    cent_id = get_centroid(geopack)
    
    df1 = by_location(cent_id, group)    

    site_info(db_filename,geopack, df1)
    
if __name__ == '__main__':
    main()
    print ("Done!")