import os
import json
import urllib
import wget
import music21
import requests
import tqdm
import shutil
import glob
import xml.dom.minidom
import xml.etree.ElementTree as ET
import time

from concurrent.futures import ProcessPoolExecutor, as_completed

PDF_PATH = 'pdf'
MIDI_PATH = 'midi'
MSCZ_PATH = 'mscz'
XML_PATH = 'mxl'
SVG_PATH = 'svg'
METADATA_PATH = 'metadata'

MUSESCORE_MAX_PAGES = 100   # MuseScore's API limit is 100

def loadCredentials(jsonFile):
    cred = None
    with open(jsonFile) as inputFile:
        cred = json.load(inputFile)

    if cred is None:
        raise ValueError("JSON file loading error")

    return cred

def callAPI(endpoint, method='GET', params={}, consumer_key=None):
    session = requests.Session()

    if consumer_key is None:
        raise ValueError("Expected consumer key, but none is given")

    params['oauth_consumer_key'] = consumer_key

    r = session.request(method,
                        endpoint,
                        params=params,
                        timeout=90,
                        files=None)

    return r

def searchScores(cred, filename='scores.xml'):
    xmlFile = xml.dom.minidom.Document()
    baseElement = xmlFile.createElement('scores')
    endpoint = 'http://api.musescore.com/services/rest/score.xml'

    for page_num in tqdm.tqdm(range(0, MUSESCORE_MAX_PAGES+1)):
        params = {
            'text': '',
            'part': 0,
            'parts': 1,
            'page': page_num,
            'license': 'to_play',
            'sort': 'view_count'
        }
        response = callAPI(endpoint, params=params, consumer_key=cred['client_key'])
        xmlContent = xml.dom.minidom.parseString(response.content)
        scores_list = xmlContent.getElementsByTagName('score')
        for score in scores_list:
            baseElement.appendChild(score)

    writer = open(filename, 'w')
    baseElement.writexml(writer)
    writer.close()

def getScore(score_id, score_secret, save_dir=XML_PATH, format='xml'):
    url = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(score_id, score_secret, format)
    try:
        response = wget.download(url, os.path.join(save_dir, '{:}_{:}.{:}'.format(score_id, score_secret, format)))
    except:
        response = None
        print("Can't download {:}_{:}.{:}".format(score_id, score_secret, format))
        pass
    
    return response

def getXMLs(scores_XML, save_dir=XML_PATH, format='xml'):
    tqdm_bar = tqdm.tqdm(scores_XML)
    for score_XML in tqdm_bar:
        score_id = score_XML.find('id').text
        score_secret = score_XML.find('secret').text
        tqdm_bar.set_description("Get ({:},{:})".format(score_id, score_secret))
        if os.path.exists(os.path.join(save_dir, '{:}_{:}.{:}'.format(score_id, score_secret, format))):
            continue
        else:
            response = getScore(score_id, score_secret, save_dir, format)


def parallel_process(array, function, n_jobs=12, use_kwargs=False, front_num=3):
    #We run the first few iterations serially to catch bugs
    if front_num > 0:
        front = [function(**a) if use_kwargs else function(a) for a in array[:front_num]]
    #If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs==1:
        return front + [function(**a) if use_kwargs else function(a) for a in tqdm(array[front_num:])]
    #Assemble the workers
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        #Pass the elements of array into function
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(function, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        #Print out the progress as tasks complete
        for f in tqdm.tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    #Get the results from the futures. 
    for i, future in tqdm.tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out

if __name__ == '__main__':
    cred = loadCredentials('MuseScoreAPI/credentials.json')
    
    if not os.path.exists('scores.xml'):
        searchScores(cred, 'scores.xml')

    if not os.path.exists(XML_PATH):
        os.mkdir(XML_PATH)

    tree = ET.parse('scores.xml')
    root = tree.getroot()
    scores_XML = root.getchildren()

    getXMLs(scores_XML, MSCZ_PATH, 'mscz')
    
    """
    xml_paths = sorted(glob.glob(os.path.join(XML_PATH, '*.mxl')))

    if not os.path.exists(PDF_PATH):
        os.mkdir(PDF_PATH)

    if not os.path.exists(MIDI_PATH):
        os.mkdir(MIDI_PATH)

    if not os.path.exists(SVG_PATH):
        os.mkdir(SVG_PATH)

    def f(xml_path):
        try:
            filename = os.path.splitext(os.path.basename(xml_path))[0]
            c = music21.converter.parse(xml_path)
            c = c.expandRepeats()

            # Write MIDI file
            response_MIDI = c.write('midi', os.path.join(MIDI_PATH, filename + '.mid'))

            # Write PDF file
            response_PDF = c.write('musicxml.pdf')
            shutil.move(response_PDF, os.path.join(PDF_PATH, filename + '.pdf'))

            # Write SVG file
            response_LY = c.write('lilypond', fp=os.path.join(SVG_PATH, filename + '.svg'))
            response_SVG = c.write('lilypond.svg', fp=os.path.join(SVG_PATH, filename))
            os.remove(os.path.join(SVG_PATH, filename))
            os.remove(os.path.join(SVG_PATH, filename + '.svg'))

            return 1
        except:
            if os.path.exists(os.path.join(MIDI_PATH, filename + '.mid')):
                os.remove(os.path.join(MIDI_PATH, filename + '.mid'))

            if os.path.exists(os.path.join(PDF_PATH, filename + '.pdf')):
                os.remove(os.path.join(PDF_PATH, filename + '.pdf'))

            return 0

    output = parallel_process(xml_paths, f)

    counter = 0
    for i in output:
        if i == 0:
            counter += 1

    print(counter)
    """
        
     
