# pylint: disable=invalid-name
"""
datasetDownloader is a Python script to pull about 2000 solo piano
sheet music from MuseScore API. The MuseScore's API credentials
must be obtained in prior to running this script.
"""
import os
import json
import xml.dom.minidom
import xml.etree.ElementTree as ET
import wget
import requests
import tqdm

PDF_PATH = 'pdf'
MIDI_PATH = 'midi'
MSCZ_PATH = 'mscz'
XML_PATH = 'mxl'
SVG_PATH = 'svg'
METADATA_PATH = 'metadata'

MUSESCORE_MAX_PAGES = 100   # MuseScore's API limit is 100


def loadCredentials(jsonFile):
    """
    This function loads a JSON file that stores API's credentials.
    """
    credFile = None
    with open(jsonFile) as inputFile:
        credFile = json.load(inputFile)

    if credFile is None:
        raise ValueError("JSON file loading error")

    return credFile


def callAPI(endpoint, method='GET', params=None, consumer_key=None):
    """
    This function calls a MuseScore's API.
    """
    if params is None:
        params = {}

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


def searchScores(cred_dict, filename='scores.xml'):
    """
    This function searches for sheet music on MuseScore's server
    and stores information in an XML file specified by `filename`.
    """
    xmlFile = xml.dom.minidom.Document()
    baseElement = xmlFile.createElement('scores')
    endpoint = 'http://api.musescore.com/services/rest/score.xml'

    for page_num in tqdm.tqdm(range(0, MUSESCORE_MAX_PAGES + 1)):
        params = {
            'text': '',
            'part': 0,
            'parts': 1,
            'page': page_num,
            'license': 'to_play',
            'sort': 'view_count'
        }
        response = callAPI(
            endpoint,
            params=params,
            consumer_key=cred_dict['client_key'])
        xmlContent = xml.dom.minidom.parseString(response.content)
        scores_list = xmlContent.getElementsByTagName('score')
        for score in scores_list:
            baseElement.appendChild(score)

    writer = open(filename, 'w')
    baseElement.writexml(writer)
    writer.close()


def getScore(score_id, score_secret, save_dir=XML_PATH, fileFormat='xml'):
    """
    This function loads a single file from MuseScore's server.
    """
    url = 'http://static.musescore.com/{:}/{:}/score.{:}'.format(
        score_id, score_secret, fileFormat)
    try:
        response = wget.download(
            url, os.path.join(
                save_dir, '{:}_{:}.{:}'.format(
                    score_id, score_secret, fileFormat)))
    except BaseException:
        response = None
        print(
            "Can't download {:}_{:}.{:}".format(score_id, score_secret, fileFormat))

    return response


def getXMLs(scores_XML, save_dir=XML_PATH, fileFormat='xml'):
    """
    This function loads all files provided in `scores_XML` from the
    MuseScore's server.
    """
    tqdm_bar = tqdm.tqdm(scores_XML)
    for score_XML in tqdm_bar:
        score_id = score_XML.find('id').text
        score_secret = score_XML.find('secret').text
        tqdm_bar.set_description(
            "Get ({:},{:})".format(
                score_id, score_secret))
        if os.path.exists(
                os.path.join(save_dir, '{:}_{:}.{:}'.format(score_id, score_secret, fileFormat))):
            continue
        else:
            getScore(score_id, score_secret, save_dir, fileFormat)

if __name__ == '__main__':
    cred = loadCredentials('MuseScoreAPI/credentials.json')

    if not os.path.exists('scores.xml'):
        searchScores(cred, 'scores.xml')

    if not os.path.exists(XML_PATH):
        os.mkdir(XML_PATH)

    tree = ET.parse('scores.xml')
    root = tree.getroot()
    XML = root.getchildren() # pylint: disable=deprecated-method

    getXMLs(XML, MSCZ_PATH, 'mscz')
