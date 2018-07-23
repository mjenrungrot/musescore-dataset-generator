import glob
import os
import tqdm
import lxml.etree
from parallel_utils import parallel_process

# Set environment variable to prevent QXcbConnection: Could not connect to display problem
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

if not os.path.exists('xml'):
  os.mkdir('xml') 

def f(mscz_path):
  filename = os.path.splitext(os.path.basename(mscz_path))[0]
  os.system("musescore {:} -r 300 -f -o xml/{:}.xml".format(mscz_path, filename))
  try:
    lxml.etree.parse("xml/{:}.xml".format(filename))
  except lxml.etree.XMLSyntaxError:
    os.remove("xml/{:}.xml".format(filename))
  
  return 0

mscz_paths = glob.glob('mscz/*.mscz')
parallel_process(mscz_paths, f)
