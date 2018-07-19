import os
import json
import urllib
from MuseScoreAPI.MuseScoreAPI import MuseScoreAPI

PDF_PATH = 'pdf'
MIDI_PATH = 'midi'
XML_PATH = 'xml'
METADATA_PATH = 'metadata'

api = MuseScoreAPI(client_key='musichackday')

# Obtain list of solo piano score
scores_list = []
params = {
    'text': '',
    'part': 0,   # Focus only on piano scores
    'parts': 1,  # Focus only on solo scores
    'page': 0,
    'license': 'to_play',
}
r = api.request('score', params)
# TODO: Extend scores_list with the response from the API
# TODO: Repeat the list of scores until reaching the last page

if not os.path.exists(PDF_PATH):
    os.mkdir(PDF_PATH)

if not os.path.exists(MIDI_PATH):
    os.mkdir(MIDI_PATH)

if not os.path.exists(PDF_PATH):
    os.mkdir(MIDI_PATH)

if not os.path.exists(METADATA_PATH):
    os.mkdir(METADATA_PATH)

# Construct the dataset
# TODO: Obtain ID and secret
for score in scores_list:
    score_id = score['id']
    secret = score['secret']
    filename = score_id

    # TODO: Check metadata (.json)
    with open(filename + '.json', 'w') as outfile:
        json.dump(score, outfile)

    # TODO: Check PDF (*.pdf)
    path = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(score_id, secret, 'pdf')
    urllib.urlretrieve(path, filename + '.pdf')

    # TODO: Check MIDI (*.mid)
    path = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(score_id, secret, 'mid')
    urllib.urlretrieve(path, filename + '.mid')

    # TODO: Check MusicXML (*.mxl)
    path = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(score_id, secret, 'mxl')
    urllib.urlretrieve(path, filename + '.mxl')

    # TODO: Try on the first score 
    break
