
"Name:"

"Description:"

"Minimum Requirements:",

"Inputs:"

"Outputs:",

"Author:",

"Created:",

import os 
import glob
import pandas as pd
from sqlalchemy import create_engine
import chardet

def csvImporter(path):
    
    engine = create_engine('postgresql://postgres:HuufDorf13!@W19-PostGIS:5432/echoes')
    extension = 'csv'
    os.chdir(path)
    reply = glob.glob('*.{}'.format(extension))
    print(reply)

    for name in reply:
        filename = os.path.splitext(name)[0]
        with open(name, 'rb') as f:
            result = chardet.detect(f.read())
            print(name,result['encoding'])
        df = pd.read_csv(name, encoding=result['encoding'])
        df.to_sql(filename, engine, schema='workpackage3', if_exists = 'replace', index=False)

def main():

    path = r"D:\Projects\Active\Intereg_Echeos\Accession_folder_Google_Drive\Workpackage_3\drive-download-20201130T162911Z-001"

    csvImporter(path)

if __name__ == "__main__":
    # only run this if this is the start up script and not imported
    main()
    print ("Done!")

