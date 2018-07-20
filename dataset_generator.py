import os
import json
import urllib
import wget
import music21
import requests
import tqdm
import xml.dom.minidom
import xml.etree.ElementTree as ET
import time

PDF_PATH = 'pdf'
MIDI_PATH = 'midi'
XML_PATH = 'xml'
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
            'page': 100,
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

def getScore(score_id, score_secret):
    url = 'http://static.musescore.com/{:}/{:}/score.mxl'.format(score_id, score_secret)
    response = wget.download(url, os.path.join(XML_PATH, '{:}_{:}.mxl'.format(score_id, score_secret)))
    time.sleep(3)

if __name__ == '__main__':
    cred = loadCredentials('MuseScoreAPI/credentials.json')
    
    if not os.path.exists('scores.xml'):
        searchScores(cred, 'scores.xml')

    tree = ET.parse('scores.xml')
    root = tree.getroot()
    scores_XML = root.getchildren()
    tqdm_bar = tqdm.tqdm(scores_XML)
    for score_XML in tqdm_bar:
        score_id = score_XML.find('id').text
        score_secret = score_XML.find('secret').text
        tqdm_bar.set_description("Get ({:},{:})".format(score_id, score_secret))
        getScore(score_id, score_secret)
    
# api = MuseScoreAPI(client_key='musichackday')

# # Obtain list of solo piano score
# scores_list = []
# params = {
#     'text': '',
#     'part': 0,   # Focus only on piano scores
#     'parts': 1,  # Focus only on solo scores
#     'page': 0,
#     'license': 'to_play',
# }
# r = api.request('score', params)
# # TODO: Extend scores_list with the response from the API
# # TODO: Repeat the list of scores until reaching the last page

# if not os.path.exists(PDF_PATH):
#     os.mkdir(PDF_PATH)

# if not os.path.exists(MIDI_PATH):
#     os.mkdir(MIDI_PATH)

# if not os.path.exists(XML_PATH):
#     os.mkdir(XML_PATH)

# if not os.path.exists(METADATA_PATH):
#     os.mkdir(METADATA_PATH)

# # Construct the dataset
# for score in scores_list:
#     score_id = score['id']
#     secret = score['secret']
#     filename = score_id

#     # TODO: Check metadata (.json)
#     with open(filename + '.json', 'w') as outfile:
#         json.dump(score, outfile)

#     # TODO: Check MusicXML (*.mxl)
#     path = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(score_id, secret, 'mxl')
#     urllib.urlretrieve(path, os.path.join(XML_PATH, filename + '.mxl'))

#     # Parse XML file
#     c = music21.converter.parse(os.path.join(XML_PATH, filename + '.mxl'))

#     # Unfold all repeat signs
#     c = c.expandRepeats()

#     # Write MIDI file
#     response_MIDI = c.write('midi', os.path.join(MIDI_PATH, filename + '.mid'))

#     # Write PDF file
#     response_PDF = c.write('musicxml.pdf')
#     os.rename(response_PDF, os.path.join(PDF_PATH, filename + '.pdf'))

#     # Write newly processed XML file
#     response_XML = c.write('xml', os.path.join(XML_PATH, filename + '.xml'))

#     # TODO: Try on the first score 
#     break
