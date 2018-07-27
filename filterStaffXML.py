# pylint: disable=invalid-name
"""
filterStaffXML contains a Python script for filter XML files
so that the resulting XML is guaranteed that each strip contains
only 2 stafflines, e.g. like solo piano sheet music.
"""
import glob
import os
import music21
from parallel_utils import parallel_process

def f(xml_path):
    """
    A function for processing a single XML file specified by
    the xml_path
    """
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
