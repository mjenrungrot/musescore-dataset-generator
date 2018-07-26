import glob
import os
import tqdm
import music21
import lxml.etree as le
from parallel_utils import parallel_process


def f(xml_path):
    delete = False
    try:
        c = music21.converter.parse(xml_path)
    except music21.musicxml.xmlToM21.MusicXMLImportException:
        delete = True

    if not delete:
        pages = music21.layout.divideByPages(c)
        for page in pages.pages:
            strips = page.systems
            for strip in strips:
                staves = strip.staves
                if len(staves) != 2:
                    delete = True
                    break
            if delete:
                break

    if delete:
        print("Remove {:}".format(xml_path))
        os.remove(xml_path)

xml_paths = glob.glob('xml/*.xml')
parallel_process(xml_paths, f)
