# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 11:48:26 2023

@author: Dick
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
from owslib.wfs import WebFeatureService
from owslib.util import openURL
from shapely.ops import nearest_points
import numpy as np
from scipy.spatial import cKDTree
import json
import csv



class img_project:
    ''' this class uses an image directory, a csv file containing names and locations of the images, and a shapefile 
    to remove all image files in the directroy which are not in the scope of the shapefile'''
    def read_csv_to_geoseries(self,filepath, shp_path,img_dir):
        image_names = []
        # read csv and convert to geoseries
        if filepath.endswith(".csv"):
            print("reading csv")
            df = pd.read_csv(filepath)
            print(len(df))
            geometry = [Point(xyz) for xyz in zip(df['Origin (Easting[m]'], df['Northing[m]'],df["Height[m])"])]
            self.geo_df = gpd.GeoSeries(geometry, index=df["Filename"])
            self.geo_df.index.name = df.index.name
            # read shapefile and return polygon object
            self.gdf = gpd.read_file(shp_path)
            # clip csv coordinate dataframe to 
            self.geo_df = gpd.clip(self.geo_df,self.gdf)
            print(len(self.geo_df))
            for image_name in self.geo_df.index:
                image_names.append(image_name)
                
            for filename in os.listdir(img_dir):
                if filename not in image_names:
                    os.remove(os.path.join(img_dir,filename))
            #         print(f'Removed {filename} from {img_dir}')
            '''if you want to visually check the point files'''
            # fig, ax = plt.subplots(figsize=(10, 10))

            #  # Plot the polygon on the axis
            # self.gdf.plot(ax=ax, alpha=0.5, edgecolor='black')

            #  # Plot the points on the axis
            # self.geo_df.plot(ax=ax, color='red', markersize=10)

            #  # Set the title of the plot
            # ax.set_title('Points and Polygon')

            #  # Show the plot
            # plt.show()
            return self.geo_df.to_file("D:/img_project/clipped.shp"), self.geo_df 
        
        elif filepath.endswith(".txt"):
            self.filetype = "textfile"
            print("reading .txt for inside")
            df = pd.read_csv(filepath, header= None)
            geometry = [Point(xyz) for xyz in zip(df[1],df[2],df[3])]
            self.geo_df = gpd.GeoSeries(geometry, index = df[0])
            self.gdf = gpd.read_file(shp_path)
            fig, ax = plt.subplots(figsize=(10, 10))

              # Plot the polygon on the axis
            self.gdf.plot(ax=ax, alpha=0.5, edgecolor='black')

              # Plot the points on the axis
            self.geo_df.plot(ax=ax, color='red', markersize=10)

              # Set the title of the plot
            ax.set_title('Points and Polygon')

              # Show the plot
            plt.show()
            return self.geo_df
        
    def clip_csv(self,photos_loc, shp_path, img_dir):
        # create list of image names
        image_names = []
        ## loading shapefiles and clipping
        photos_loc = gpd.read_file(photos_loc)
        # read shapefile and return polygon object
        boundary = gpd.read_file(shp_path)
        # clip csv coordinate dataframe to 
        clipped_photo_loc = gpd.clip(photos_loc,boundary)
        print(len(clipped_photo_loc))
        
        # renaming operation
        if "new_name" in photos_loc.columns:
            #iterate over rows of clipped photo locations
            for index, row in clipped_photo_loc.iterrows():
                i = 0
                # add the basename of the file location to the 
                image_names.append(os.path.basename(row[37]))
                print(row[37])
                if os.path.exists(row[37]):
                    if row["new_name"]:
                        print(row[37])
                        print(row["new_name"])
                        new_path = img_dir+row["new_name"]+".jpg"
                        while os.path.isfile(new_path):
                            i += 1
                            newer_path = img_dir+row["new_name"]+"_"+str(i)+".jpg"
                            if not os.path.isfile(newer_path):
                                os.rename(old_path, newer_path)
                        else:  
                            os.rename(row[37],new_path)
        else: 
            for index, row in clipped_photo_loc.iterrows():
                
                image_names.append(os.path.basename(row[37]))
                print(os.path.basename(row[37]))
                
        
            
        for filename in os.listdir(img_dir):
            if filename not in image_names:
                os.remove(os.path.join(img_dir,filename))
            else:
                print("file "+filename+" stays")
       
        
        
    
    def punten_thin(self):
    
        
        # Create an empty list to store the thinned points
        thinned_points = []
        
        # Set the initial point to the first point in the GeoSeries
        last_point = self.geo_df.iloc[0].geometry
        thinned_points.append(last_point)
        
        # Loop through each point in the GeoSeries
        for i in range(1, len(self.geo_df)):
            current_point = self.geo_df.iloc[i].geometry
            
            # Calculate the distance between the current point and the last point
            distance = last_point.distance(current_point)
            
            # If the distance is greater than 5 meters, add the current point to the thinned points list
            if distance >= 10:
                thinned_points.append(current_point)
                
                # Set the last point to the current point
                last_point = current_point
        
        # Create a new GeoDataFrame from the thinned points list
        thinned_points_gdf = gpd.GeoDataFrame({'geometry': thinned_points})
        self.geo_df = gpd.GeoSeries(thinned_points_gdf['geometry'])
        
        # Save the thinned points GeoDataFrame to a new file
        thinned_points_gdf.to_file('thinned_points.shp')
        return self.geo_df
    
    def get_wfs(self): #,shp_path):
        # create the bounding box for the clip
        xmin,ymin,xmax,ymax = self.gdf.total_bounds
        self.bbox=(xmin,ymin,xmax,ymax)
        print(self.bbox)
        # get features from webfeature server
        wfs = WebFeatureService("https://geo.rijkswaterstaat.nl/services/ogc/gdr/kerngis_droog/ows?service=WFS&request=getcapabilities&version=2.0.0", version = "2.0.0")
        weghectometrering=wfs.getfeature('kerngis_droog:hectometerborden', bbox = self.bbox, outputFormat="json")
        data = json.loads(weghectometrering.read())
        self.hectometrering = gpd.GeoDataFrame.from_features(data['features'])
        return 
    
        
    def ckdnearest(self):
        '''' returns a csv file of the geomtery dataframe of the images and the nearest hectometer paal in a csv format'''
        # open dataframes as numpy arrays containing x and y coordinates
        nA = np.array(list(self.geo_df.geometry.apply(lambda x: (x.x, x.y))))
        nB = np.array(list(self.hectometrering.geometry.apply(lambda x: (x.x, x.y))))
        # build a decision tree for the hectometrering
        btree = cKDTree(nB)
        # query the tree with a 1 number neighbour distance 
        dist, idx = btree.query(nA, k=1)
        # build a new geodataframe containing all ids, distances and hectometer metadata
        gdB_nearest = self.hectometrering.iloc[idx].drop(columns="geometry").reset_index(drop=True)
        if self.filetype != "textfile":
            self.gdf = pd.concat(
                [
                    self.geo_df.reset_index(drop=True),
                    gdB_nearest,
                    pd.Series(dist, name='dist')
                ], 
                axis=1)
        else:
            df = pd.DataFrame(self.geo_df.index.values)
            self.gdf = pd.concat([df,gdB_nearest],axis=1)
        # save output to csv
        self.gdf.to_csv("closest_points.csv")
        return self.gdf
    
    
    def rename(self,img_dir,new_jpg_dir,filepath):
        ''' renames all image files in input directory to columns of the csv file created in ckdnearest function '''
        # check if the output path exists and make output path if not
        if not os.path.exists(new_jpg_dir):
            os.mkdir(new_jpg_dir)
        # open csv file from ckdnearest    
        with open("closest_points.csv", "r") as f:
            reader = csv.reader(f)
            data = list(reader)
            # sort data
            data = sorted(data, key= lambda x : x[15])
        with open(filepath, "r") as s:
             reader = csv.reader(s)
             locations = list(reader)
        
        # body of function, check for id match, contruct new name from columns, rename file to new location
        for path in os.listdir(img_dir):
            i = 0
            for row in data:
                for loc in locations: 
                    if self.filetype == "textfile":
                        filename = row[1]+".jpg"
                       
                        
                        if os.path.basename(path) == filename== loc[0]+".jpg":
                            try:
                                old_path = os.path.join(img_dir, path).replace("//","/")
                                # row 14 = A, row 13 = 4, row 15 = 77.4, row 16 = n, row 18 = Li/Re, output = a4 77.4 n Li.jpg
                                new_name = row[13]+ row[12]+" " +row[14]+" "+ row[15]+" "+ row[17]+".jpg"
                                row[1] = new_name
                                new_path = os.path.join(new_jpg_dir, new_name).replace("//", "/")
                                while os.path.isfile(new_path):
                                    i += 1
                                    new_name = row[13]+ row[12]+" " +row[14]+" "+ row[15]+" "+ row[17]+"_"+str(i)+ ".jpg"
                                    newer_path = os.path.join(new_jpg_dir, new_name).replace("//", "/")
                                    if not os.path.isfile(newer_path):
                                        os.rename(old_path, newer_path)
                                        row.append(newer_path)
                                        loc.append(os.path.basename(newer_path))
                                else:    
                                    os.rename(old_path, new_path)
                                    row.append(new_path)
                                    loc.append(os.path.basename(new_path))
                                    i = 0
                            except:
                                pass
                    else:                                
                        if os.path.basename(path) == filename:
                            try:
                                old_path = os.path.join(img_dir, path).replace("//","/")
                                # row 14 = A, row 13 = 4, row 15 = 77.4, row 16 = n, row 18 = Li/Re, output = a4 77.4 n Li.jpg
                                new_name = row[14]+ row[13]+" " +row[15]+" "+ row[16]+" "+ row[18]+".jpg"
                                row[1] = new_name
                                new_path = os.path.join(new_jpg_dir, new_name).replace("//", "/")
                                while os.path.isfile(new_path):
                                    i += 1
                                    new_name = row[14]+ row[13]+" " +row[15]+" "+ row[16]+" "+ row[18]+"_"+str(i)+ ".jpg"
                                    newer_path = os.path.join(new_jpg_dir, new_name).replace("//", "/")
                                    if not os.path.isfile(newer_path):
                                        os.rename(old_path, newer_path)
                                        row.append(os.path.basename(newer_path))
                                else:    
                                    os.rename(old_path, new_path)
                                    row.append(os.path.basename(new_path))
                                    i = 0
                            except:
                                pass
        locationsdf= pd.DataFrame(locations)
        locationsdf.to_csv("locations_renamed.csv")
        datagdf = gpd.GeoDataFrame(data)
        datagdf.to_csv("closest_points_renamed.csv")                    
                    

        

        
img_proj.clip_csv("D:/img_project/Drechttunnel/Drecht_photos_loc.shp","D:/img_project/Drechttunnel/Drecht_scannen_LOD350.shp","D:/img_project/Drechttunnel/output/")
img_proj = img_project()
img_proj.read_csv_to_geoseries("D:/imgs_static/sijtwende_statisch/vliettunnel/zb/panorama2/Station position.txt","D:/img_project/Sijtwendetunnel/binnen/Sijtwende_drone_LOD200.shp","D:\imgs_static\old_names\panorama2_vt_zd_sijt")
img_proj.get_wfs()
img_proj.ckdnearest()
img_proj.rename("D:\imgs_static\old_names\panorama2_vt_zd_sijt","D:\imgs_static\old_names\panorama2_vt_zd_sijt/output","D:/imgs_static/sijtwende_statisch/vliettunnel/zb/panorama2/Station position.txt")
# img_proj.check()

print(locations)
for name in os.listdir("D:/imgs_static/old_names"):
    print(name)