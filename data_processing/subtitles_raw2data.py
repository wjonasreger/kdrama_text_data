"""
subtitles_raw2data.py -- process raw subtitles data into structured data for later processing and analysis installments

Python (c) 2023 Jonas Reger (students tea)

Created: February 20, 2023 (orig. August 7, 2022)
Modified: February 21, 2023
"""

#### import packages ####
import os, re, sys, shutil
import pandas as pd
import unicodedata
import hgtk

sys.path.append("..")
from lib.conv2csv import xml2csv, vtt2csv, srt2csv
from lib.utils import createPath, cleanName, checkTarget, cleanHangul, auxText



def main():
    #### set parameters ####
    raw_path = '../raw/' # source data path
    subraw_path = '../raw/subtitles' # source data subtitles path
    data_path = '../data' # target data path
    subdata_path = '../data/subtitles' # target data subtitles path

    show_ids_path = '../data/show_ids.csv' # show id data path (name, id dictionary)
    show_info_path = '../data/show_info.csv' # show info data path (other info)
    src_batch_082022_path = '../raw/082022_batch_info.csv' # source batch 082022 meta data
    trg_batch_082022_path = '../data/082022_batch_info.csv' # target batch 082022 meta data

    ignore = ['.DS_Store', '.ipynb_checkpoints'] # file types or directories to ignore in processing

    # create target data directories
    createPath(data_path)
    createPath(subdata_path)



    #### search source data ####
    # search relevant files
    raw_list, dir_list = [], []
    for root, dirs, files in os.walk(subraw_path):
        for dr in dirs:
            dir_list.append(dr)
        for file in files:
            if file not in ignore:
                raw_list.append(os.path.join(root, file))
            else:
                os.remove(os.path.join(root, file))

    # process path data into dataframe
    item_info = []
    for i in range(len(raw_list)):
        # raw file info
        file_path = raw_list[i]
        file_info = file_path.split('/') # / for mac or \\ for windows

        # clean name for regex pattern
        special_reps = {'?':'\?', '(':'\(', ')':'\)'}
        name = ''.join([ special_reps.get(c, c) for c in file_info[3] ]) # show name
        pattern = name + '(_)(.*?).(xml|srt|vtt)' # pattern of file name
        file_pattern_rs = re.compile(pattern)

        # search for patterns
        search_results = file_pattern_rs.search(file_path)
        if search_results: # save pattern matches
            item_info.append( [file_path, file_info[3]] + [ search_results[2], search_results[3] ] )
        else: # ignore non-matches
            pass

    # basic file info dataframe
    column_names = ['raw_src', 'raw_name', 'raw_item_id', 'file_type']
    df_info = pd.DataFrame(item_info, columns=column_names)

    # decompose raw_item_id into season and episode ids
    item_rs = re.compile('[s]([\d]*)[e]([\d]*)')
    raw_item_id_extract = df_info.raw_item_id.str.extractall(item_rs).reset_index(drop=True) # extract info
    df_info['season'] = raw_item_id_extract[0]
    df_info['episode'] = raw_item_id_extract[1]

    # list of shows
    dir_series = pd.Series(dir_list)



    #### process show info data ####
    # load in existing data or create empty dataframe if not exist
    is_exist = os.path.exists(show_ids_path)
    df_show_ids = pd.read_csv(show_ids_path) if is_exist else pd.DataFrame(columns=['name', 'id'])

    # find max id in data
    max_id_value = df_show_ids.id.apply(lambda x: x[1:]).astype(int).max()
    max_id_value = -1 if max_id_value != max_id_value else max_id_value

    # lists of shows
    failed_add_list = dir_series[ dir_series.isin(df_show_ids.name) ] # already in show id data
    new_add_list = dir_series[ ~dir_series.isin(df_show_ids.name) ] # not in show id data

    # adding new shows to data
    data = {'name': [], 'id': []}
    for i in range(len(new_add_list)):
        data['name'].append( new_add_list.values[i] )
        data['id'].append( f'R{i + max_id_value + 1:03d}' )

    data['name'] = sorted(data['name'])
    df_show_ids_data = pd.DataFrame(data)

    # merge show id data (and save)
    df_show_ids = pd.concat( [df_show_ids, df_show_ids_data], axis=0 ).reset_index(drop=True)
    df_show_ids.to_csv(show_ids_path, index=False)
    df_show_info = df_info.merge(df_show_ids, left_on='raw_name', right_on='name', how='left')
    df_show_info['item_id'] = df_show_info.apply(lambda x: f'{x.id}-S{int(x.season):02d}-T{int(x.episode):03d}', axis=1) # create item ids
    df_show_info.to_csv(show_info_path, index=False)



    #### file conversions ####
    # add any subtitle file path to list for preprocessing
    subdata_list = []
    for root, dirs, files in os.walk(subdata_path):
        for file in files:
            if file not in ignore:
                subdata_list.append(os.path.join(root, file))

    # convert xml/vtt/srt files to pooled csv doc for each show item
    for id in range(len(set(df_show_info.id))):
        id = f'R{id:03d}'
        trg_path = subdata_path + '/' + str(id) + '.csv'

        # process data if not processed yet, skip data that is done
        if trg_path not in subdata_list:
            df_temp = df_show_info.iloc[list(df_show_info.id == id), :].reset_index(drop=True)
            show_subtitle_data = pd.DataFrame()

            # convert files
            for item in range(len(df_temp)):
                item_id = df_temp.loc[item, 'item_id']
                raw_src = df_temp.loc[item, 'raw_src']
                file_type = df_temp.loc[item, 'file_type']
                if file_type == 'xml':
                    transformed_data = xml2csv(raw_src, item_id)
                elif file_type == 'vtt':
                    transformed_data = vtt2csv(raw_src, item_id)
                elif file_type == 'srt':
                    transformed_data = srt2csv(raw_src, item_id)
                else:
                    print(f'[FAILED] {item_id}')

                if len(transformed_data) < 3:
                    print(item_id)

                show_subtitle_data = pd.concat([show_subtitle_data, transformed_data], axis=0)

            # clean texts
            fn_prep_verbal = lambda text: "" if any( [checkTarget(x, text.lower()) for x in ['netflix', 'viki']] ) else cleanHangul( auxText(text)['text'] )
            fn_prep_read = lambda text: "" if any( [checkTarget(x, text.lower()) for x in ['netflix', 'viki']] ) else cleanHangul( text )
            show_subtitle_data["prep_verbal"] = show_subtitle_data.text.apply(fn_prep_verbal)
            show_subtitle_data["prep_read"] = show_subtitle_data.text.apply(fn_prep_read)

            show_subtitle_data.to_csv(trg_path, index=False)



    #### process batch 082022 meta data ####
    # load in data from raw directory
    df_batch_082022 = pd.read_csv(src_batch_082022_path)[['English', 'Korean', 'Other', 'CC SRC', 'Genres', 'Link', 'IMDb']]
    temp = df_show_ids.sort_values(by='name').reset_index(drop=True) # prep to merge id and meta data

    # clean names for matching
    df_batch_082022['reg_name'] = df_batch_082022.English.apply(lambda x: cleanName(x) )
    df_batch_082022['show_id'] = '---'

    # align data to merge
    for i in range(len(df_batch_082022)):
        name = df_batch_082022.loc[i, 'reg_name']
        name_in_id = temp.name.isin([name])
        if sum(name_in_id) == 1:
            df_batch_082022.loc[i, 'show_id'] = temp.loc[temp.name == name, 'id'].values[0]
            df_batch_082022.loc[i, 'show_name'] = temp.loc[temp.name == name, 'name'].values[0]

    ## save batch_082022 to data
    df_batch_082022_tosave = df_batch_082022.copy()
    df_batch_082022_tosave.drop('reg_name', axis=1, inplace=True)
    df_batch_082022_tosave = df_batch_082022_tosave[['show_id', 'show_name', 'English', 'Korean', 'Other', 'Genres', 'CC SRC', 'Link', 'IMDb']]
    df_batch_082022_tosave.columns = ['show_id', 'show_name', 'english', 'korean', 'other', 'genres', 'cc_src', 'url', 'imdb']

    df_batch_082022_tosave.to_csv(trg_batch_082022_path)
    
if __name__ == "__main__":
    main()