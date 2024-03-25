"""
conv2csv.py -- convert various subtitle file formats to .csv

Python (c) 2023 Jonas Reger (students tea)

Created: February 20, 2023 (orig. August 7, 2022)
Modified: February 21, 2023
"""

#### import packages ####
from bs4 import BeautifulSoup # need `pip install lxml`
import re
import pandas



#### conversion functions ####

# Convert Netflix XML to CSV
def xml2csv(input_file, input_id):
    with open(input_file, encoding='utf8') as file:
        xml_text = file.read()
        soup = BeautifulSoup(xml_text, "xml")
    soup_text_p = soup.findAll('p')
    tickrate = soup.find_all('tt')[0].get('ttp:tickRate')

    data_xml = {
        'begin': [],
        'end': [],
        'id': [],
        'text': []
    }

    num_rc = re.compile('\D+')
    for i, j in enumerate(soup_text_p):
        data_xml['begin'].append( round( int(num_rc.sub('', j['begin'])) / int(tickrate), 3 ) )
        data_xml['end'].append( round( int(num_rc.sub('', j['end'])) / int(tickrate), 3 ) )
        data_xml['id'].append( f"{input_id}-U{int(num_rc.sub('', j['xml:id'])):06d}" )
        data_xml['text'].append( j.text )

    df_xml = pandas.DataFrame(data_xml)
    return(df_xml)

# Convert Viki VTT to CSV
def vtt2csv(input_file, input_id):
    with open(input_file, encoding='utf8') as file:
        vtt_text = file.read()

    newline_rc = re.compile('\n\n')
    space_rc = re.compile('\n')
    num_rc = re.compile('\D+')
    
    vtt_text = newline_rc.split(vtt_text)
    for i in range(len(vtt_text)):
        vtt_text[i] = space_rc.split(vtt_text[i])

    data_vtt = {
        'begin': [],
        'end': [],
        'id': [],
        'text': []
    }

    for i in vtt_text:
        if len(i) > 2:
            try:
                if re.compile(' --> ').search( i[1] )[0]:
                    times = i[1].split(' --> ')
                    begin = sum( float(j) * 60 ** i for i, j in enumerate(reversed(times[0].split(':'))) )
                    end = sum( float(j) * 60 ** i for i, j in enumerate(reversed(times[1].split(':'))) )
                id = f"{input_id}-U{ int(num_rc.sub('', i[0])) :06d}"
                text = ' '.join(i[2:])

                data_vtt['begin'].append( begin )
                data_vtt['end'].append( end )
                data_vtt['id'].append( id )
                data_vtt['text'].append( text )
            except:
                pass

    df_vtt = pandas.DataFrame(data_vtt)
    return(df_vtt)

# Convert OpenSub SRT to CSV
def srt2csv(input_file, input_id):
    with open(input_file, encoding='utf8') as file:
        srt_text = file.read()

    newline_rc = re.compile('\n\n')
    space_rc = re.compile('\n')
    num_rc = re.compile('\D+')

    srt_text = newline_rc.split(srt_text)
    for i in range(len(srt_text)):
        srt_text[i] = space_rc.split(srt_text[i])

    data_srt = {
        'begin': [],
        'end': [],
        'id': [],
        'text': []
    }

    for i in srt_text:
        if len(i) > 2:
            try:
                if re.compile(' --> ').search( i[1] )[0]:
                    times = i[1].replace(',', '.').split(' --> ')
                    begin = sum( float(j) * 60 ** i for i, j in enumerate(reversed(times[0].split(':'))) )
                    end = sum( float(j) * 60 ** i for i, j in enumerate(reversed(times[1].split(':'))) )
                id = f"{input_id}-U{ int(num_rc.sub('', i[0])) :06d}"
                text = ' '.join(i[2:])

                data_srt['begin'].append( begin )
                data_srt['end'].append( end )
                data_srt['id'].append( id )
                data_srt['text'].append( text )
            except:
                pass

    df_srt = pandas.DataFrame(data_srt)
    return df_srt