# pylint: disable=invalid-name
"""
MXLtoXML is a Python script for converting all MXL files to XML files.
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


def f(mxl_path):
    """
    This function converts a single MXL file to a single XML file.
    The XML invalid file is ignored.
    """
    filename = os.path.splitext(os.path.basename(mxl_path))[0]
    subprocess.call(
        "musescore {:} -r 300 -f -o xml/{:}.xml".format(mxl_path, filename),
        shell=False)
    try:
        lxml.etree.parse("xml/{:}.xml".format(filename)) # pylint: disable=c-extension-no-member
    except lxml.etree.XMLSyntaxError: # pylint: disable=c-extension-no-member
        os.remove("xml/{:}.xml".format(filename))

    return 0


mxl_paths = glob.glob('mxl/*.mxl')
parallel_process(mxl_paths, f)
