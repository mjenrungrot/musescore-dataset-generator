import os
import json
import urllib
import music21
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

if not os.path.exists(XML_PATH):
    os.mkdir(XML_PATH)

if not os.path.exists(METADATA_PATH):
    os.mkdir(METADATA_PATH)

# Construct the dataset
for score in scores_list:
    score_id = score['id']
    secret = score['secret']
    filename = score_id

    # TODO: Check metadata (.json)
    with open(filename + '.json', 'w') as outfile:
        json.dump(score, outfile)

    # TODO: Check MusicXML (*.mxl)
    path = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(score_id, secret, 'mxl')
    urllib.urlretrieve(path, os.path.join(XML_PATH, filename + '.mxl'))

    # Parse XML file
    c = music21.parse(os.path.join(XML_PATH, filename + '.mxl'))

    # Unfold all repeat signs
    c = c.expandRepeats()

    # Write MIDI file
    response_MIDI = c.write('midi', os.path.join(MIDI_PATH, filename + '.mid'))

    # Write PDF file
    response_PDF = c.write('pdf', os.path.join(PDF_PATH, filename + '.pdf'))

    # Write newly processed XML file
    response_XML = c.write('xml', os.path.join(XML_PATH, filename + '.xml'))

    # TODO: Try on the first score 
    break
