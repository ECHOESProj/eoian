"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

from datetime import datetime

import pandas as pd
import requests


# Retrieve the data from the csv
def get_data(test_filename):
    data = pd.read_csv(test_filename)

    return (data)


# Converts API call into list
def show_data(W_data):
    temp = W_data['main']['temp']
    feels_like = W_data['main']['feels_like']
    humidity = W_data['main']['humidity']
    wind_speed = W_data['wind']['speed']
    latitude = W_data['coord']['lat']
    longitude = W_data['coord']['lon']
    description = W_data['weather'][0]['description']
    a = temp, wind_speed, latitude, longitude, description, feels_like, humidity

    return a


# Retrieve the data for a set location -- Data is returned as an array and then to a dataframe
def by_location(test_filename):
    data = get_data(test_filename)
    group = []
    for j, i in enumerate(data['Lng']):
        # print(data['Lat'].values[j],data['Lng'].values[j])
        url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=81f5a3465ec3abf5ce734c45ef519ef4&units=metric'.format(
            data['Lat'].values[j], data['Lng'].values[j])
        res = requests.get(url)
        W_data = res.json()
        # print(W_data)
        a = show_data(W_data)
        # print(a)
        group.append(a)
    df2 = pd.DataFrame(data=group)
    df2.columns = ['temp', 'wind_speed', 'latitude', 'longitude', 'description', 'feels_like', 'humidity']
    # print(df2)

    return df2


# Merges dataframe and fits time stamps - Exports output as an excel
def merge_export_tabls(output_filename, sheet_name, test_filename):
    data = get_data(test_filename)
    df = by_location(test_filename)
    data.insert(0, 'Id', data.index + 1)
    df.insert(0, 'Id', df.index + 1)
    df3 = pd.merge(data, df, on='Id')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y")
    tme_string = now.strftime("%H:%M:%S")
    df3["Date"] = dt_string
    df3["Time"] = tme_string
    print(df3)
    df3.to_excel(output_filename, sheet_name=sheet_name, index=False)


def main():
    test_filename = r"\\CAOIMHIN10\Projects\Active\Intereg_Echeos\API_text\API_test_location.csv"

    output_filename = r'\\CAOIMHIN10\Projects\Active\Intereg_Echeos\API_text\API_test1.xlsx'

    sheet_name = 'OpenWeatherMap'

    merge_export_tabls(output_filename, sheet_name, test_filename)


if __name__ == '__main__':
    main()
    print("Done!")
