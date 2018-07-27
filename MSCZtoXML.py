# pylint: disable=invalid-name
"""
MSCZtoXML is a Python script that converts all mscz files to XML files.
"""
import glob
import os
import subprocess
import lxml.etree
from parallel_utils import parallel_process

# Set environment variable to prevent QXcbConnection: Could not connect to
# display problem
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

if not os.path.exists('xml'):
    os.mkdir('xml')

def f(mscz_path):
    """
    This function converts a single mscz file to an XML file.
    The XML file that is parsed incorrectly is ignored.
    """
    filename = os.path.splitext(os.path.basename(mscz_path))[0]
    subprocess.call(
        "musescore {:} -r 300 -f -o xml/{:}.xml".format(mscz_path, filename),
        shell=False)
    try:
        lxml.etree.parse("xml/{:}.xml".format(filename)) # pylint: disable=c-extension-no-member
    except lxml.etree.XMLSyntaxError: # pylint: disable=c-extension-no-member
        os.remove("xml/{:}.xml".format(filename))

    return 0


mscz_paths = glob.glob('mscz/*.mscz')
parallel_process(mscz_paths, f)
