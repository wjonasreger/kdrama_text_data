"""
utils.py -- general utility functions for KoNLP2

Python (c) 2023 Jonas Reger (students tea)

Created: February 21, 2023
Modified: February 21, 2023
"""

#### import packages ####
import os, re, sys, shutil
import pandas as pd
import unicodedata
import hgtk



#### basic functions ####
# check if target x is in y
def checkTarget(x, y):
    return True if x in y else False

# check if x is None
def isNone(x):
    return x != x



#### text cleaning ####
# converts the unicode file to ascii
def unicodeToASCII(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

# clean hangul texts
def cleanHangul(w):
    w = re.sub(r'([?.!,\(\)\[\]])', r' \1 ', w) # adding space between letters and special characters
    tmp_w = []
    for t in w.split(' '):
        tt = ''.join( [c if (hgtk.checker.is_hangul(c) | (c in '?.!,')) else '' for c in t] ) # clean hangul texts
        tmp_w.append(tt)
    w = ' '.join(tmp_w)
    w = re.sub(r'[" "]+', ' ', w) # remove excess white space
    w = unicodeToASCII(w.lower().strip())
    return w

# function to clean show names
def cleanName(string, clean_path = False):
    # lower case, implement regex updates
    target = string.lower().strip()
    pattern = '[<>:"|?*#\-\',!()]' if clean_path else '[<>:"|?*#\-\',!().]'
    target = re.sub(pattern, '', target)
    target = re.sub('[\s]+', ' ', target)
    target = re.sub(' ', '_', target)

    return target

# matches subtitles texts that are nonverbal (i.e., in () or [])
def auxText(input_text):
    bracket_pattern = r'[\(|\[]([^\(\[\]\)]*)[\)|\]]'
    matches = re.finditer(bracket_pattern, input_text)
    groups = []
    content = []
    for matchNum, match in enumerate(matches, start=1):
        groups.append( match.group() )
        for groupNum in range(0, len(match.groups())):
            groupNum += 1
            content.append( match.group(groupNum) )

    strip_text = input_text
    for g in list(set(groups)):
        strip_text = strip_text.replace(g, '')

    return {'input': input_text, 'text':strip_text, 'content':content}



#### path functions ####
# function to create directory if not exist, remove and create if exist, or do nothing if exists
def createPath(path, remove=False):
    if not os.path.isdir(path):
        os.makedirs(path)
    elif remove:
        shutil.rmtree(path)
        os.makedirs(path)
        
# function to clean path names
def cleanPath(src_root, src_leaf, is_dir=False):
    # lower case, implement regex updates
    trg_leaf = cleanName(src_leaf, clean_path = True)

    # special handling of . character since files have extensions
    pattern = '[.]' if is_dir else '[.](?=.*[.])'
    trg_leaf = re.sub(pattern, '', trg_leaf)

    # rename path
    source = os.path.join(src_root, src_leaf)
    target = os.path.join(src_root, trg_leaf)
    os.rename(source, target)
    return target
