"""
clean_filenames.py -- script to clean or normalize directory/file names in raw subtitles data for easier access and processing

Python (c) 2023 Jonas Reger (students tea)

Created: February 20, 2023
Modified: February 21, 2023
"""

#### import packages ####
import os, re, sys

sys.path.append("..")
from lib.utils import cleanPath



def main():
    #### set parameters ####
    subraw_path = '../raw/subtitles' # source subtitles data path

    # regex
    ignore = ['.DS_Store', '.ipynb_checkpoints'] # files/dirs to ignore
    # sep = '/\\'
    # repl_dict = {' ': '_'}
    # repl_regex = re.compile("|".join(repl_dict.keys()))



    #### clean directory and file names in raw sub data ####
    # walk through directory to rename directories
    for root, dirs, files in os.walk(subraw_path):
        for dr in dirs:
            trg = cleanPath( root, dr, is_dir=True )

    # walk through directory to rename files
    file_list = []
    for root, dirs, files in os.walk(subraw_path):
        for file in files:
            # ignore certain files (remove them if ignored)
            if file not in ignore:
                trg = cleanPath( root, file )
                file_list.append(trg)
            else:
                os.remove(os.path.join(root, file))

    # printout
    print(f"{len(file_list)} files found.")
    for i in range(5):
        print(file_list[i])
    
    
if __name__ == "__main__":
    main()