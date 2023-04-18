import sys
import os
import github_action_utils as gha_utils

# Read the command-line argument passed to the interpreter when invoking the script
files = sys.argv[1]

print(files)

fileList= files.split(",")

folders = {}
foldersOutput = ""
for file in fileList:
    print(file)
    folder = file.split('/')[1].strip()
    if folder not in foldersOutput:
        if (len(foldersOutput) > 0):
            foldersOutput += " "
        foldersOutput += folder
gha_utils.set_output("folders", foldersOutput)