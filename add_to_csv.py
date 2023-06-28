import os
import csv
from PIL import Image
import geopandas as gpd

# Path to the two folders containing images
folder1_path = "D:/imgs_static/old_names/panorama_vt_zd_Sijt"

folder2_path = "D:/imgs_static/sijtwende_statisch/vliettunnel/zb/panorama/output"

# Path to the CSV file to store the results
csv_path ="D:/imgs_static/sijtwende_statisch/vliettunnel/zb/panorama/Station position.txt"

# Open the CSV file for writing
with open(csv_path, 'r') as csvfile:
    writer = csv.reader(csvfile)
    data = list(writer)
    print(data)
    print("read data")
    for row in data:
        print(f"read {row[0]}")
        # Iterate over images in the first folder
        for filename1 in os.listdir(folder1_path):
            print(filename1)
            if row[0]+".jpg" == filename1:
                print("read{row}")
                if filename1.endswith('.jpg'):
                    # Open the first image and get its size
                    image1_path = os.path.join(folder1_path, filename1)
                    with Image.open(image1_path) as image1:
                        print(f"opening {filename1}")
                        size1 = image1.size
    
                    # Find a matching image in the second folder
                    for filename2 in os.listdir(folder2_path):
                        
                        # Open the second image and get its size
                        image2_path = os.path.join(folder2_path, filename2)
                        with Image.open(image2_path) as image2:
                            print(f"opening {filename2}")
                            size2 = image2.size
    
                        # Check if the sizes match
                        if size1 == size2:
                            print(f"new name = {filename2}")
                            # If the sizes match, add the second image name to the CSV file
                            row.append(filename2)
                            break
    datagdf = gpd.GeoDataFrame(data)
    datagdf.to_csv("sijt_vt_renamed_3.csv")
