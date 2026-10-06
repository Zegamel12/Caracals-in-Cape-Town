import os
#import functions.py as functions

#if not os.path.exists(directory):
 #   os.makedirs(directory)


from src.step01_download import download_gps_data

# donwload gps data
gps_data = download_gps_data()