import glob
import os
import tqdm
import lxml.etree
from parallel_utils import parallel_process

# Set environment variable to prevent QXcbConnection: Could not connect to display problem
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

if not os.path.exists('xml'):
  os.mkdir('xml') 

def f(mxl_path):
  filename = os.path.splitext(os.path.basename(mxl_path))[0]
  os.system("musescore {:} -r 300 -f -o xml/{:}.xml".format(mxl_path, filename))
  try:
    lxml.etree.parse("xml/{:}.xml".format(filename))
  except lxml.etree.XMLSyntaxError:
    os.remove("xml/{:}.xml".format(filename))
  
  return 0

mxl_paths = glob.glob('mxl/*.mxl')
parallel_process(mxl_paths, f)

