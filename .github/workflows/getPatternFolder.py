import sys
import os

# Read the command-line argument passed to the interpreter when invoking the script
files = sys.argv[1]

print(files)

fileList= files.split(",")

folders = {}
for file in fileList:
    print(file)
    folder = file.split('/')[1].strip()
    if folder not in folders:
        folders[folder] = ""
print(folders.keys())