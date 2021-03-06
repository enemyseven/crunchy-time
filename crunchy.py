#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Crunchy Time
Author: Cody Hill
Date Created: March 10, 2021
Last Modified: May 10, 2021
This Software is released under the MIT License:
http://www.opensource.org/licenses/mit-license.html
See LICENSE at root of project for more details.
(C) 2021 Cody Hill
"""
import time
import os
import subprocess
import glob

VERSION = '0.0.5'

# MARK: Global Variables

# Executables
ffmpeg = "./ffmpeg"
ffprobe = "./ffprobe"

# Directories
inputPath = "./input/"
outputPath = "./output/"

# MARK: Functions

def setup():
    # Make sure things are good to go.
    if not os.path.isfile(ffmpeg):
        print("Error:\tffmpeg not found.")
        exit()

    # Check to see if input directory exists.
    if not os.path.isdir(inputPath):
        # If not exit...
        print("Error:\tInput directory not found.")
        exit()
        
    # Check to see if output directory exists.
    if not os.path.isdir(outputPath):
        # If not create it.
        os.makedirs(outputPath)

def isLandscape(input):
    execute = [
            ffprobe,
            '-v',
            'error',
            '-select_streams',
            'v:0',
            '-show_entries',
            'stream=width,height',
            '-of',
            'csv=s=x:p=0',
            f'{input}', # input filename
    ]
    result = subprocess.run(execute, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Get rid of binary encoding and trailing newline
    resolution = str(result.stdout.decode('UTF-8')).rstrip()
    width, height = str(resolution).split('x')
    print(width)
    print(height)
    if int(width) > int(height):
        return True
    else:
        return False
    
def makePreview(input, output):
    if not os.path.isfile(output):
        landscape = [
            ffmpeg,
            '-i', input, # Input filename
            '-ss', '0:00:03', # Skip ahead to
            '-to', '0:00:13', # copy until
            '-filter:v',
            'fps=15, crop=ih/3*4:ih, scale=320:240, format=yuv420p, eq=gamma=0.8:brightness=-0.3:saturation=0.2', # filter chain
            '-an', # Do not extract audio
            f'{output}', # output filename
            '-y' # overwrite output if it exists
        ]
        portrait = [
            ffmpeg,
            '-i', input, # Input filename
            '-ss', '0:00:03', # Skip ahead to
            '-to', '0:00:13', # copy until
            '-filter:v',
            #'fps=15, crop=iw:iw/4*3, scale=320:240, format=yuv420p, eq=brightness=-0.3:saturation=0.6', # filter chain
            'fps=15, crop=iw:ih*0.65, scale=-1:240, pad=320:ih:(ow-iw)/2, format=yuv420p, eq=gamma=0.8:brightness=-0.3:saturation=0.2',
            '-an', # Do not extract audio
            f'{output}', # output filename
            '-y' # overwrite output if it exists
        ]
        
        if isLandscape(input):
            execute = landscape
        else:
            execute = portrait
            
        try:
            subprocess.run(execute, check=True)
        except subprocess.CalledProcessError as e:
            print("Early exit on file ", input , " due to error.")
            exit()
    else:
        print("Warning: ", output, " already exits.")

def getFilenames(directory):
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(".mp4")]
    return filtered_files

def main():
  setup()
  
  # Get files
  filenames = getFilenames(inputPath)
  
  # Note start time
  start = time.time()
  
  # Process files
  for filename in filenames:
    if filename == "\n":
        print("Encountered newline.")
        break
        
    # Make target input
    input = inputPath + filename

    # Make target output
    pre, ext = os.path.splitext(filename)
    output = outputPath + pre + "-preview.mp4"
    pre, ext = os.path.splitext(input)
    
    makePreview(input, output)
    
  # Output time spent
  end = time.time()
  totalTime = end - start
  print("\n\n--- Complete ---")
  print("Total time: " + str(totalTime))


if __name__ == "__main__":
    # execute only if run as a script
    main()
