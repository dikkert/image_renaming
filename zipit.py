# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 10:27:34 2023

@author: Dick
"""


import os
import zipfile

def zip_files(files, max_size):
    

    '''The `zip_files()` function is designed to zip files from a specified directory into multiple zip files based on a maximum size limit.
    
    ## Function Signature
    
    ```python
    def zip_files(files, max_size):
        pass
    ```
    
    ## Parameters
    
    - `files` (str): The path to the directory containing the files to be zipped.
    - `max_size` (int): The maximum size limit (in bytes) for each zip file.
    '''

    # Create a new zip file
    zip_num = 1
    zip_name = f"files_{zip_num}.zip"
    zip_file = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    total_size = 0
    
    # Add files to the zip file
    for file in os.listdir(files):
        
        file_size = os.path.getsize(file)
        if total_size + file_size > max_size:
            # Close the current zip file and start a new one
            zip_file.close()
            zip_num += 1
            zip_name = f"files_{zip_num}.zip"
            zip_file = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
            total_size = 0
        zip_file.write(file)
        total_size += file_size
    
    # Close the final zip file
    zip_file.close()

 
for file in os.listdir("D:/img_project/Drechttunnel/output"):
    print(file)